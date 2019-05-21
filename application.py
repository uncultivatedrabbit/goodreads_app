import os

from flask import Flask, session, render_template, request, redirect, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import apology, login_required

app = Flask(__name__)

# Goodreads API key 
# key: 0xmaANE2lcYXcf5I9m6xqw

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # verify a username was inputted
        if not request.form.get("username"):
            return apology("HAHAHA INPUT YOUR USERNAME")
        elif not request.form.get("password"):
            return apology("WHAT'S YOUR PASSWORD")
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Password must match, try again")
        flash("registered")
        return render_template("index.html")
    else:    
        return render_template("register.html")
