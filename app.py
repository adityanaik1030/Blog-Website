from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import psycopg2

# variable to check whether admin is logged in or not
admin_logged_in = False

app = Flask(__name__)

# Create Database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://exuberant_diaries_user:3WnU9mIxQX7gx7DLikvF2fEYoFYnRCa3@dpg-cj9q03pduelc73d663fg-a.singapore-postgres.render.com/exuberant_diaries"

# postgres://exuberant_diaries_user:3WnU9mIxQX7gx7DLikvF2fEYoFYnRCa3@dpg-cj9q03pduelc73d663fg-a.singapore-postgres.render.com/exuberant_diaries
#

# Create the extension
db = SQLAlchemy()

# initialise the app with the extension
db.init_app(app)


class Blog(db.Model):
    #  String: maximum length of the string is limited to 250 characters
    # Text: which allows for storing large amounts of text data, typically much longer than 250 characters.
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.String)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    # Query to select all the posts from the DB
    # all_posts = db.session.execute(db.select(Blog)).scalars()
    # all_posts = db.session.execute(db.session(Blog).order_by(Blog.date))
    all_posts = db.session.query(Blog).order_by(desc(Blog.date))
    return render_template("index.html", posts=all_posts, admin_logged_in=admin_logged_in)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        if request.form.get("email") == "admin@gmail.com" and request.form.get("password") == "admin":
            global admin_logged_in
            admin_logged_in = True
            # return render_template("index.html", admin_logged_in=admin_logged_in)
            return redirect(url_for("home", admin_logged_in=admin_logged_in))
        else:
            return render_template("not_found.html")


@app.route('/logout')
def logout():
    global admin_logged_in
    admin_logged_in = False
    return redirect(url_for("home", admin_logged_in=admin_logged_in))


@app.route('/add-post', methods=["GET", "POST"])
def add_new_post():
    if request.method == "GET":
        return render_template("createblog.html")
    else:
        # Calculating Date with the help of datetime class present in datetime module.
        # %B: month name, %d: day like 1-31, %Y: year
        now = datetime.now()
        date = now.strftime("%B %d, %Y")
        new_post = Blog(
            title=request.form.get("title"),
            subtitle=request.form.get("subtitle"),
            body=request.form.get("body"),
            date=date
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("home"))


@app.route('/show-post<int:post_id><int:is_logged_in>')
def show_post(post_id, is_logged_in):
    post = db.session.execute(db.select(Blog).where(Blog.id == post_id)).scalar()
    return render_template("show_post.html", post=post, is_logged_in=is_logged_in)


@app.route('/update-post<int:post_id><int:is_logged_in>', methods=["GET", "POST"])
def update_post(post_id, is_logged_in):
    if request.method == "GET":
        post = db.session.execute(db.select(Blog).where(Blog.id == post_id)).scalar()
        return render_template("update.html", post=post)
    else:
        now = datetime.now()
        date = now.strftime("%B %d, %Y")
        post = db.session.execute(db.select(Blog).where(Blog.id == post_id)).scalar()
        post.title = request.form.get("title")
        post.subtitle = request.form.get("subtitle")
        post.body = request.form.get("body")
        post.date = date
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id, is_logged_in=is_logged_in))


@app.route('/delete<int:post_id>')
def delete_post(post_id):
    post = db.session.execute(db.select(Blog).where(Blog.id == post_id)).scalar()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
