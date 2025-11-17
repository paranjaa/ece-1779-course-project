import os
import secrets
from logging.config import dictConfig

import psycopg
from dotenv import load_dotenv
from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_wtf import CSRFProtect
from markupsafe import escape

from forms import EmptyForm
from forms import LoginForm
from forms import EnrollmentForm
from utils import roles

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from functools import wraps

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
# Local development .env file
if os.path.isfile("./.env"):
    load_dotenv()

for secret_file in ["DB_NAME_FILE", "DB_USER_FILE", "DB_PASSWORD_FILE", "APP_SECRET_KEY_FILE"]:
    if os.getenv(secret_file) is not None:
        # using docker secrets in docker swarm instead of loading a .env context
        with open(os.path.join("/run/secrets/", os.getenv(secret_file)), "r") as fh:
            os.environ[secret_file.replace("_FILE","")] = fh.read()

if os.getenv("APP_SECRET_KEY") is not None:
    app.secret_key = os.getenv("APP_SECRET_KEY")
else:
    app.secret_key = secrets.token_urlsafe(32)

csrf = CSRFProtect(app)


def get_db_connection():
    conn = psycopg.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn


def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if that user isn't in the session, then kick them back to the login
        if 'username' not in session:
            # TODO: Make sure these messages are working, correctly?
            flash('Login is required for this page', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# role based access to particular routes
def require_role(allowed_roles: list[roles]):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                if roles(session.get('role')) not in allowed_roles:
                    return "Forbidden", 403
            except ValueError:
                return "Forbidden", 403
            return f(*args, **kwargs)

        return decorated

    return wrapper


@app.route('/')
@require_login
def index():
    # displays all items, so need to run that command first

    # adding a parameter for what to sort by, default is by ID
    # and another one for sorting order

    # TODO: Add sorting by location and category as well
    sort_by = request.args.get('sort_by', 'id')
    # should default to ascending
    order = request.args.get('order', 'asc')

    if sort_by not in ['item_name', 'item_quantity', 'id']:
        sort_by = 'id'

    if order not in ['asc', 'desc']:
        # probably won't be invalid, just in case
        order = 'asc'

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, item_name, item_quantity FROM inventory ORDER BY {sort_by} {order};")
            items = cur.fetchall()

    # adding a blank form so it can at least load
    form = EmptyForm()

    return render_template('dashboard.html', items=items, sort_by=sort_by, order=order, form=form)


# adding a route for adding items from the dashboard
# remaking this from backend ones (in case I do it wrong)
@app.route('/add_item', methods=['POST'])
@require_login
@require_role([roles.MANAGER, roles.ADMIN])
def add_item():
    # read in the results from the form fields
    item_name = request.form.get("item_name")
    item_quantity = request.form.get("item_quantity")

    if item_name and item_quantity:
        try:
            # TODO: add error checking to this (duplicate names) (empty fields)
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO inventory (item_name, item_quantity)
                        VALUES (%s, %s)
                        ON CONFLICT (item_name) DO UPDATE SET
                            item_quantity = inventory.item_quantity + EXCLUDED.item_quantity;
                        """,
                        (item_name, item_quantity)
                    )
                    conn.commit()

            app.logger.info(f"Added/updated item '{item_name}' with quantity {item_quantity}.")
        except Exception as e:
            app.logger.error(f"Error adding item: {e}")
    # reload the page (should show the new item in the display)
    return redirect(url_for('index'))


# adding a route for removing a particular item from the dashboard
@app.route('/delete_item/<int:item_id>', methods=['POST'])
@require_login
@require_role([roles.MANAGER, roles.ADMIN])
def delete_item(item_id):
    """
    Dashboard endpoint for deleting an item from the database
    :param item_id: The item id to be deleted
    :return:
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # TODO: (verifying the item exists) (warnings for deleting an item)

                cur.execute(
                    """
                    DELETE FROM inventory 
                        WHERE id = %s;
                    """,
                    (item_id,)
                )
                conn.commit()

            if cur.rowcount > 0:
                app.logger.info(f"Deleted item with ID {item_id}")
            else:
                app.logger.info(f"Item with ID {item_id} does not exist.")
    except Exception as e:
        app.logger.error(f"Error deleting item: {e}")
    return redirect(url_for('index'))


@app.route('/increment/<int:item_id>', methods=['POST'])
@require_login
def increment(item_id):
    """
    Dashboard endpoint for incrementing the item count
    :param item_id: The item id whose quantity is to be incremented
    :return:
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE inventory 
                    SET item_quantity = item_quantity + 1 
                    WHERE id = %s 
                    RETURNING item_quantity;
                """,
                (item_id,)
            )
            result = cur.fetchone()
            conn.commit()

    app.logger.info(f"Incremented item {item_id} to {result[0]}")
    return redirect(url_for('index'))


@app.route('/decrement/<int:item_id>', methods=['POST'])
@require_login
def decrement(item_id):
    """
    Dashboard endpoint for decrementing the item count
    :param item_id: The item id whose quantity is to be decremented
    :return:
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                # additional check here to make sure that it doesn't set an item to a negative value
                """
                UPDATE inventory 
                    SET item_quantity = GREATEST(item_quantity - 1, 0) 
                    WHERE id = %s 
                    RETURNING item_quantity;
                """,
                (item_id,)
            )
            result = cur.fetchone()
            conn.commit()

    app.logger.info(f"Decremented item {item_id} to {result[0]}")
    return redirect(url_for('index'))



@app.route('/enroll', methods=['GET', 'POST'])
@require_login
@require_role([roles.ADMIN])
def enroll():
    form = EnrollmentForm()

    # TODO: Add error checking for this, some way of making sure values are unique
    # that and the user roles, but that's later
    if form.validate_on_submit():
        username = escape(form.username.data)
        password = escape(form.password.data)
        role = escape(form.role.data)

        # store the user password as a hash rather than plain
        password_hash = generate_password_hash(password)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                            INSERT INTO users (username, password, role) 
                                VALUES (%s, %s, %s)
                        """,
                        (username, password_hash, role)
                    )
                    conn.commit()
                    # if the form works, then take them to the login page
                    flash(f"Enrolled a new user {username} with role {role}", "Success")
                    return redirect(url_for('index'))
                except Exception as e:
                    flash("Invalid entry. Try again.", "error")
                    app.logger.error(f"Error signing up new user: {e}")

    return render_template('enroll.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = escape(form.username.data)
        password = escape(form.password.data)

        # check login credentials from the database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT password, role FROM users
                        WHERE username = %s
                    """,
                    (username,)
                )
                result = cur.fetchone()

        if result and check_password_hash(result[0], password):
            app.logger.info(f"{result[1]} {username} logged in.")
            session['username'] = username
            session['role'] = result[1]
            flash("Login successful", "success")
            return redirect(url_for("index"))
        else:
            app.logger.info("Failed login attempted.")
            flash("Invalid username or password", "danger")
            return render_template("login.html", form=form, error="Invalid username or password")
    return render_template("login.html", form=form)


@app.route('/inventory', methods=['GET', 'POST', 'PUT', 'DELETE'])
def inventory():
    app.logger.info(request)
    # Only allow logged-in users to access this page
    if "username" in session:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                if request.method == 'GET':
                    # SELECT - return the inventory
                    cur.execute(
                        """
                        SELECT * from inventory
                        """
                    )
                    posts = cur.fetchall()
                    app.logger.info("Fetched all rows in inventory.")
                    return (str(posts), 200)

                elif request.method == 'POST':
                    # INSERT - insert a new item into the DB if it does not exist or
                    #          does nothing if it does exist
                    item_name = request.form.get("item_name")
                    item_quantity = request.form.get("item_quantity")
                    if (item_name is not None) and (item_quantity is not None):
                        item_name = escape(item_name)
                        item_quantity = escape(item_quantity)
                        try:
                            cur.execute(
                                """
                                INSERT INTO inventory (item_name, item_quantity)
                                    VALUES (%s, %s)
                                    --ON CONFLICT (item_name) DO UPDATE SET 
                                    --    item_quantity = inventory.item_quantity + excluded.item_quantity
                                    RETURNING id;
                                """,
                                (item_name, item_quantity)
                            )
                        except psycopg.errors.lookup("23505") as e:
                            # Uniqueness constraint violation
                            # Attempting to insert an item with a name that has already been used
                            app.logger.info(f"Did not insert non-unique item \"{item_name}\".")
                            return ("Cannot POST an item that has already been INSERTED. Did you mean PUT?", 409)

                        db_results = cur.fetchone()[0]
                        app.logger.info(
                            f"Inserted new entry with id \"{db_results}\", item name \"{item_name}\", and item quantity \"{item_quantity}\".")
                        return (str(db_results), 201)

                    else:
                        app.logger.info("Missing item name or item quantity.")
                        return ("Missing item name or item quantity.", 400)

                elif request.method == 'PUT':
                    # UPDATE - update an existing item in the DB by adding the new quantity to the
                    #          current quantity
                    item_name = request.form.get("item_name")
                    item_quantity = request.form.get("item_quantity")
                    if (item_name is not None) and (item_quantity is not None):
                        item_name = escape(item_name)
                        item_quantity = escape(item_quantity)
                        cur.execute(
                            """
                            UPDATE inventory
                                SET item_quantity = item_quantity + %s
                                WHERE item_name = %s
                                RETURNING *;
                            """,
                            (item_quantity, item_name)
                        )
                        db_results = cur.fetchone()
                        if db_results is not None:
                            app.logger.info(f"Updated item \"{item_name}\" to new quantity \"{db_results[2]}\".")
                            return (str(db_results), 200)
                        else:
                            app.logger.info(f"Item \"{item_name}\" does not exist.")
                            return (f"Item \"{item_name}\" does not exist.", 404)

                    else:
                        app.logger.info("Missing item name or item quantity.")
                        return ("Missing item name or item quantity.", 400)

                # Only allow managers to delete items from the DB
                elif request.method == 'DELETE':
                    if session["username"] == "manager":
                        # DELETE - delete an existing item from the DB
                        item_name = request.form.get("item_name")

                        if item_name is not None:
                            item_name = escape(item_name)
                            cur.execute(
                                """
                                DELETE FROM inventory
                                    WHERE item_name = %s;
                                """,
                                (item_name,)
                            )
                            if cur.rowcount > 0:
                                app.logger.info(f"Item \"{item_name}\" has been deleted.")
                                return ("", 204)
                            else:
                                app.logger.info(f"Item \"{item_name}\" does not exist.")
                                return (f"Item \"{item_name}\" does not exist.", 404)
                        else:
                            app.logger.info("Missing item name or item quantity.")
                            return ("Missing item name or item quantity.", 400)
                    else:
                        return ("Authorization required. Contact your manager to perform this action.", 403)
    else:
        return redirect(url_for("login"))


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
