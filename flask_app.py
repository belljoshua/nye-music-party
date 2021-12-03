from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)

app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="joshbell",
    password="mysqlpassword",
    hostname="joshbell.mysql.pythonanywhere-services.com",
    databasename="joshbell$music-party",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User (db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    phone = db.Column(db.String(15))
    date_added = db.Column(db.Date, default=datetime.now)

class Song (db.Model):
    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    artist = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', foreign_keys=category_id)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', foreign_keys=user_id)
    year = db.Column(db.Integer)
    added = db.Column(db.Date, default=datetime.now)


class Category (db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    added = db.Column(db.Date, default=datetime.now)

class YearCategory (db.Model):
    __tablename__ = "yearcategories"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', foreign_keys=category_id)
    added = db.Column(db.Date, default=datetime.now)


##### Serves as Page Layout
@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        if "error" in request.args:
            return render_template("main_page.html", users=User.query.all(), error="True")
        return render_template("main_page.html", users=User.query.all())

@app.route("/selection", methods=["GET", "POST"])
def selection():
    if request.method == "GET":
        user_id = request.args.get("users_list", "no value")
        user = User.query.get(user_id)
        if user == None:
            return redirect(url_for('index', error="True"))
        user_songs = Song.query.filter(Song.user_id == user_id, Song.year == datetime.now().year)
        if "error" in request.args:
            return render_template(
                "song_selection.html",
                error=request.args["error"],
                user=user,
                categories=Category.query.all(),
                songs=user_songs)
        return render_template(
            "song_selection.html",
            user=user,
            categories=Category.query.all(),
            songs=user_songs)
    else:
        if Category.query.get(request.form["categories"]) == None:
            return redirect(url_for('selection', song_title=request.form["song_title"], artist=request.form["artist"], category=request.form["categories"], users_list=request.form["user"], error="Please choose a category"))
        song = Song (
                title=request.form["song_title"],
                artist=request.form["artist"],
                category_id=request.form["categories"],
                user_id=request.form["user"],
                year=datetime.now().year
            )
        db.session.add(song)
        db.session.commit()

        return redirect(url_for('selection', users_list=request.form["user"]))



if __name__=="__main__":
    app.run()

