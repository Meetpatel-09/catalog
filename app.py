from flask import Flask, render_template, redirect, url_for, request, session
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)

app.secret_key = "CATALOG_APP"

app.config['UPLOAD_FOLDER'] = 'static/uploads'

connection_string = "mysql+mysqlconnector://root:@localhost/catalog_flask"
engin = create_engine(connection_string, echo=True)


@app.route('/')
def home():

    items = []
    favourite_items = []

    query1 = "SELECT * FROM item_table"
    query2 = "SELECT item_id FROM catalog_flask.favourite_table where user_id = :user_id;"

    with engin.connect() as conn:
        result1 = conn.execute(text(query1))
        result2 = conn.execute(text(query2), {
            "user_id": session["user_id"]
        })

        for row in result1.all():
            items.append(row)

        for row in result2.all():
            favourite_items.append(row[0])

        print(favourite_items)
    return render_template('index.html', items=items, favourite_items=favourite_items, title="Home")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title="Login")
    elif request.method == 'POST':
        data = request.form

        if data['email'] == "admin@test.com" and data["password"] == "123456":
            session['admin'] = "admin"
            return redirect(url_for('home'))

        query = "SELECT * FROM user_table WHERE email = :email and password = :password"

        with engin.connect() as conn:
            result = conn.execute(text(query), {
                "email": data["email"],
                "password": data["password"]
            })

            if result.rowcount == 1:
                session['user_id'] = result.first()[0]
                return redirect(url_for('home'))

            return redirect(url_for('login'))

    return "<h1> Invalid Request</h1>"


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', title="Registration")
    elif request.method == 'POST':

        data = request.form

        query = "INSERT INTO user_table (fname, lname, email, mobile_number, password) VALUES (:fname,:lname,:email,:mobile_number,:password)"

        with engin.connect() as conn:

            result = conn.execute(text(query), {
                "fname": data["fname"],
                "lname": data["lname"],
                "email": data["email"],
                "mobile_number": data["mobile"],
                "password": data["password"]
            })

            conn.commit()

            print(result.rowcount)

            if result.rowcount == 1:
                return redirect(url_for('login'))

            return redirect(url_for('register'))

    return "<h1> Invalid Request</h1>"


@app.route('/favourites')
def favourites():

    items = []
    favourite_items = []

    query1 = "SELECT * FROM item_table"
    query2 = "SELECT item_id FROM catalog_flask.favourite_table where user_id = :user_id;"

    with engin.connect() as conn:
        result1 = conn.execute(text(query1))
        result2 = conn.execute(text(query2), {
            "user_id": session["user_id"]
        })

        for row in result1.all():
            items.append(row)

        for row in result2.all():
            favourite_items.append(row[0])

        print(favourite_items)
    return render_template('favourites.html', items=items, favourite_items=favourite_items, title="Favourites")


@app.route("/manage_items")
def manage_items():
    items = []

    query = "SELECT * FROM item_table"

    with engin.connect() as conn:
        result = conn.execute(text(query))

        for row in result.all():
            items.append(row)

    return render_template('manage_items.html', items=items, title="Manage Items")


@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        return render_template('add_item.html', title="Add Item")
    elif request.method == 'POST':

        data = request.form
        image = request.files['image']

        image_name = image.filename

        query = "INSERT INTO item_table (title, image) VALUES (:title, :image)"

        with engin.connect() as conn:

            result = conn.execute(text(query), {
                "title": data["title"],
                "image": image_name
            })

            conn.commit()

            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

            print(result.rowcount)

            if result.rowcount == 1:
                return redirect(url_for('manage_items'))

            return redirect(url_for('add_item'))

    return "<h1> Invalid Request</h1>"


@app.route("/add_to_favourite/<item_id>")
def add_to_favourite(item_id):
    query = "INSERT INTO favourite_table (user_id, item_id) VALUES (:user_id, :item_id)"

    with engin.connect() as conn:

        result = conn.execute(text(query), {
            "user_id": session["user_id"],
            "item_id": item_id
        })

        conn.commit()

    return redirect(url_for('home'))


@app.route("/remove_favourite/<item_id>")
def remove_favourite(item_id):
    query = "DELETE FROM favourite_table WHERE user_id = :user_id AND item_id = :item_id"

    with engin.connect() as conn:

        result = conn.execute(text(query), {
            "user_id": session["user_id"],
            "item_id": item_id
        })

        conn.commit()

    return redirect(url_for('home'))


@app.route("/contact_us")
def contact_us():
    return render_template("contact_us.html", title="Contact Us")


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
