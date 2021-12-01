from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

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
    date_added = db.Column(db.Date)

##### Serves as Page Layout
@app.route('/')
def page_layout():
    return render_template("main_page.html", users=User.query.all())

if __name__=="__main__":
    app.run()