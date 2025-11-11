from flask import Flask
from flask import request
from markupsafe import escape

from dotenv import load_dotenv
import psycopg
import os

from logging.config import dictConfig

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

def get_db_connection():
    conn = psycopg.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

@app.route('/')
def index():
    return "index"

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