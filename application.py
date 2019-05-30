import os

from flask import Flask, session, render_template, request, redirect, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import apology, login_required
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

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
    """ Log user in """
    session.clear()

    username=request.form.get("username")

    if request.method == "POST":
        # verify username was submitted
        if not request.form.get("username"):
            return apology("please provide a username")
        # verify password was submitted
        elif not request.form.get("password"):
            return apology("please provide a password")
        #get user information from database    
        rows= db.execute("SELECT * FROM users WHERE username = username", {"username": username})

        data = rows.fetchone()

        #verify the username and password are good to go
        if data == None or not check_password_hash(data[2], request.form.get("password")):
            return apology("Invalid username or password")
        
        session["user_id"] = data[0]
        session["user_name"] = data[1]
        
        return redirect("/")
        

    else:
        return render_template("login.html")
    
    
@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

    

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    """Register user"""
    if request.method == "POST":
        # verify a username was inputted
        if not request.form.get("username"):
            return apology("HAHAHA INPUT YOUR USERNAME")
        # verify a password was inputted
        elif not request.form.get("password"):
            return apology("WHAT'S YOUR PASSWORD")
        # verify the passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Password must match, try again")
        flash("registered")
        username = request.form.get("username")
        password = request.form.get("password")

        # inserts new user and password into the database
        db.execute("INSERT INTO users (username, password) VALUES(:username, :password)", {"username": username, "password": generate_password_hash(password)})
        db.commit();
        
        flash('Account created', 'info')

        return redirect("/login")
    else:    
        return render_template("register.html")

@app.route("/search", methods=(["GET"]))
@login_required
def search():
    return render_template("results.html", books=books)   
