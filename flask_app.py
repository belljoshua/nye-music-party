import csv
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import sys
import os

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


# Initializes the songs table from a CSV
# my_dir = os.path.dirname(__file__)
# csvpath = os.path.join(my_dir, "songs.csv")
# csvsongs = []
# with open(csvpath, mode='r', encoding="utf8") as file:
#     csvfile = csv.DictReader(file)
#     for row in csvfile:
#         csvsongs.append((row["Song"], row["Artist"], row["Year"]))

# for csvsong in csvsongs:
#     title = csvsong[0]
#     artist = csvsong[1]
#     year = csvsong[2]
#     song = Song(
#         title=title,
#         artist=artist,
#         year=year
#     )
#     db.session.add(song)
# db.session.commit()

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
        print("user_id:", user_id, file=sys.stderr)
        user = User.query.get(user_id)
        if user == None:
            return redirect(url_for('index', error="True"))
        user_songs = Song.query.filter(Song.user_id == user_id, Song.year == datetime.now().year)
        all_songs = Song.query.all()
        if "error" in request.args:
            return render_template(
                "song_selection.html",
                error=request.args["error"],
                user=user,
                categories=Category.query.all(),
                song_title=request.args["song_title"],
                artist=request.args["artist"],
                selected_category=request.args["category"],
                songs=user_songs,
                all_songs=all_songs
                )
        return render_template(
            "song_selection.html",
            user=user,
            categories=Category.query.all(),
            songs=user_songs,
            all_songs=all_songs)
    else:
        song_title = request.form["song_title"]
        artist = request.form["artist"]
        category = request.form["categories"]
        user = request.form["user"]
        error = None
        if Category.query.get(category) == None:
            error = "Please choose a category"
        elif not song_title:
            error = "Please enter a song title"
        elif not artist:
            error = "Please enter an artist"
        elif Song.query.filter_by(category_id=category, year=datetime.now().year, user_id=user).first():
            print ("query result:",Song.query.filter_by(category_id=category, year=datetime.now().year, user_id=user),file=sys.stderr)
            error = "You have already selected a song with that category"

        if error:
            return redirect(url_for('selection', song_title=song_title, artist=artist, category=category, users_list=user, error=error))

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

@app.route("/delete/song", methods=["POST"])
def deleteSong():
    song_id = request.form["delete_button"]
    Song.query.filter_by(id=song_id).delete()
    db.session.commit()
    # song = Song.query.get(song_id)
    # song.delete()
    user_id = request.form["user"]
    return redirect(url_for("selection", users_list=user_id))

if __name__=="__main__":
    app.run()

