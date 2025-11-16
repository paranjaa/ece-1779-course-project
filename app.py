from flask import Flask
from flask import request, render_template, redirect, url_for, session
from markupsafe import escape

from dotenv import load_dotenv
import psycopg
import os

from logging.config import dictConfig

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import flash

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired



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

#for managing sessions
#need to add this to env file
app.secret_key = os.getenv('SECRET_KEY')  



def get_db_connection():
    conn = psycopg.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn


class SignupForm(FlaskForm):
    username = StringField("username", validators=[InputRequired()])
    password = PasswordField("password", validators=[InputRequired()])


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignupForm()

    #TODO: Add error checking for this, some way of making sure values are unique
    # that and the user roles, but that's later
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # store the user password as a hash rather than plain      
        password_hash = generate_password_hash(password)


        with get_db_connection() as conn:
          with conn.cursor() as cur:
            try:
              cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password_hash)
              )
              conn.commit()
              #if the form works, then take them to the login page
              flash("Signed up successfully, please log in with new credientials", "Success")
              return redirect(url_for('login'))
            except Exception as e:
              flash("Invalid username or password, or some other error", "error")
              app.logger.error(f"Error signing up new user: {e}")

    return render_template('signup.html', form=form)

#enabling CSRF to secure forms
#csrf = CSRFProtect(app)



#@app.route('/login', methods=['GET', 'POST'])
#def login():
#
#
#    if request.method == 'POST':
#        username = request.form['username']
#        password = request.form['password']
#
#        with get_db_connection() as conn:
#            with conn.cursor() as cur:
#                cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
#                cur.execute("SELECT id, password, role FROM users WHERE username = %s", (username,))
#                user = cur.fetchone()
#
#        #check if the password entered matches the hash
#        if user and check_password_hash(user[1], password):
#            session['user_id'] = user[0]
#            session['username'] = username
#            session['role'] = user[2]
#            flash("Login successful", "success")
#            return redirect(url_for('index'))
#        else:
#            flash("Invalid username or password", "error")
#            return redirect(url_for('login'))
#          
#    return render_template('login.html')


class LoginForm(FlaskForm):
    username = StringField("username", validators=[InputRequired()])
    password = PasswordField("password", validators=[InputRequired()])



#TODO: Add feedback, for success and failure. Figure out how to do this in python
#and a corresponding one for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  
        username = form.username.data
        password = form.password.data

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, password, role FROM users WHERE username = %s", (username,))
                user = cur.fetchone()

        #check if the password entered matches the hash
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            flash("Login successful", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('login'))
          
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash("logged out successfully", "info")
    return redirect(url_for('login'))


#also a function for preventing access to dashboard 
#(and later, other pages) without logging in
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #if that user isn't in the session, then kick them back to the login
        if 'user_id' not in session:
             #TODO: Make sure these messages are working, correctly?
            flash('Login is required for this page', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

#role based access to particular routes
def require_role(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') != role:
                return "Forbidden", 403
            return f(*args, **kwargs)
        return decorated
    return wrapper


class EmptyForm(FlaskForm):
    pass

#adding a route for the inventory dashboard
@app.route('/')
@require_login
def index():
  #displays all items, so need to run that command first

  #adding a parameter for what to sort by, default is by ID
  #and another one for sorting order

  #TODO: Add sorting by location and category as well
  sort_by = request.args.get('sort_by', 'id')
  #should default to ascending
  order = request.args.get('order', 'asc') 

  if sort_by not in ['item_name', 'item_quantity', 'id']:
    sort_by = 'id' 

  if order not in ['asc', 'desc']:
    #probably won't be invalid, just in case
    order = 'asc'

  with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, item_name, item_quantity FROM inventory ORDER BY {sort_by} {order};")
            items = cur.fetchall()


  #adding a blank form so it can at least load
  form = EmptyForm()

  return render_template('dashboard.html', items=items, sort_by=sort_by, order=order, form=form)


#adding a route for adding items from the dashboard
#remaking this from backend ones (in case I do it wrong)
@app.route('/add_item', methods=['POST'])
@require_login
def add_item():
    #read in the results from the form fields
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
    #reload the page (should show the new item in the display)
    return redirect(url_for('index'))



#adding a route for removing a particular item from the dashboard
@app.route('/delete_item/<int:item_id>', methods=['POST'])
@require_login
def delete_item(item_id):
    try:
      with get_db_connection() as conn:
        with conn.cursor() as cur:
          # TODO: (verifying the item exists) (warnings for deleting an item)

          cur.execute("DELETE FROM inventory WHERE id = %s;", (item_id,))

          conn.commit()
        app.logger.info(f"Deleted item with ID {item_id}")
    except Exception as e:
            app.logger.error(f"Error deleting item: {e}")
    return redirect(url_for('index'))

#adding routes for incrementing and decrementing items from the dashboard
@app.route('/increment/<int:item_id>', methods=['POST'])
@require_login
def increment(item_id):
  with get_db_connection() as conn:
    with conn.cursor() as cur:
      cur.execute(
        "UPDATE inventory SET item_quantity = item_quantity + 1 WHERE id = %s RETURNING item_quantity;",
        (item_id,)
      )
      result = cur.fetchone()
      conn.commit()
  app.logger.info(f"Incremented item {item_id} to {result[0]}")
  return redirect(url_for('index'))


#same as other function
@app.route('/decrement/<int:item_id>', methods=['POST'])
@require_login
def decrement(item_id):
  with get_db_connection() as conn:
    with conn.cursor() as cur:
      cur.execute(
        #additional check here to make sure that it doesn't set an item to a negative value
        "UPDATE inventory SET item_quantity = GREATEST(item_quantity - 1, 0) WHERE id = %s RETURNING item_quantity;",
        (item_id,)
      )
      result = cur.fetchone()
      conn.commit()
  app.logger.info(f"Decremented item {item_id} to {result[0]}")
  return redirect(url_for('index'))


#@app.route('/admin')
#@require_login
#def index():
#    return "index"

@app.route('/inventory', methods=['GET', 'POST', 'PUT', 'DELETE'])
def inventory():
    print(request)
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
                    app.logger.info(f"Inserted new entry with id \"{db_results}\", item name \"{item_name}\", and item quantity \"{item_quantity}\".")
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

            elif request.method == 'DELETE':
                # DELETE - delete an existing item from the DB
                # TODO: Is this a behaviour we want though? We can either set the quantity to 0
                #       and leave the name and id in place, or we can completely remove the entry
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
