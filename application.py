import os, json

from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import apology, login_required
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

import requests

app = Flask(__name__)

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
        rows= db.execute("SELECT * FROM users WHERE username = :username", {"username": username})

        data = rows.fetchone()

        #verify the  password is good to go
        if data == None or not check_password_hash(data[2], request.form.get("password")):
            return apology("Invalid username or password")
        if request.form.get("username") != data[1]:
            return apology("Username does not match")

        
        session["user_id"] = data[0]
        session["user_name"] = data[1]
        
        return redirect("/")
        

    else:
        return render_template("login.html")
    
    
@app.route("/logout")
def logout():
    """ Log User Out """
    session.clear()
    return render_template("logout.html")

    

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    """Register user"""
    username = request.form.get("username")
    if request.method == "POST":

        # verify a username was inputted
        if not request.form.get("username"):
            return apology("HAHAHA INPUT YOUR USERNAME")

        #Check database for existing username
        checkUser = db.execute("SELECT * FROM users WHERE username = :username", 
        {"username": request.form.get("username")}).fetchone()

        if checkUser:
            return apology("That username already exists")

        # verify a password was inputted
        elif not request.form.get("password"):
            return apology("WHAT'S YOUR PASSWORD")
        # verify the passwords match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Password must match, try again")
       
        password = request.form.get("password")

        

        # inserts new user and password into the database
        db.execute("INSERT INTO users (username, password) VALUES(:username, :password)", 
        {"username": username, "password": generate_password_hash(password)})
        db.commit();
        
        flash("You have been registered!", "info")
        
        return redirect("/login")
    else:    
        return render_template("register.html")

@app.route("/search", methods=["GET"])
@login_required
def search():
    """Search Through Book Database"""
    # if they don't enter any search parameters
    if not request.args.get("book"):
        return apology("Please enter a book")

    # set up query to include anything similar to what they typed in using wildcards
    searched = "%" + request.args.get("book") + "%"
    #to uppercase 
    searched=searched.title()

    #query database for specific searched book
    rows = db.execute("SELECT isbn,title,author,year FROM books WHERE isbn LIKE :searched OR title LIKE :searched OR author LIKE :searched OR year LIKE :searched", {"searched": searched})

    #if the book isn't in the database of books return apology
    if rows.rowcount == 0:
        return apology("This book is not in our database, sorry!")
    #return all the books that match
    books = rows.fetchall()

    return render_template("results.html", books=books)


@app.route("/book/<isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    if request.method=="POST":
        # establish veriables for reviews / comment database queries
        user_id =session["user_id"]
        comment = request.form.get("comment")
        rating = request.form.get("rating")

        # find book in database
        id_row = db.execute("SELECT book_id FROM books WHERE isbn = :isbn", {"isbn": isbn})
        book_id = id_row.fetchone()
        book_id = book_id[0]

        

        submission_row = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", 
        {"user_id" : user_id, "book_id": book_id})

        if submission_row.rowcount == 1:
            flash("You already submitted a review of this book", "info")
            return redirect("/book/" + isbn)
        

        rating = int(rating)

        db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES (:user_id, :book_id, :comment, :rating)",
        {"user_id": user_id, "book_id": book_id, "comment": comment, "rating": rating})

        db.commit()
        flash("Review submitted!", "info")
        return redirect("/book/" + isbn)
    else:
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn", {"isbn": isbn})

        bookDetails = row.fetchall()

        # Get API Key to query goodreads API
        key = os.getenv("GOODREADS_KEY")
        # get the review count from goodreads 
        query = requests.get("https://www.goodreads.com/book/review_counts.json", params = {"key":key, "isbns" :isbn})
        response = query.json()
        response = response['books'][0]
        
        # add it to bookdetails 
        bookDetails.append(response)

        # dealing with user reviews

        row = db.execute("SELECT book_id FROM books WHERE isbn = :isbn", {"isbn": isbn})

        book = row.fetchone()
        book=book[0]

        # grab all the reviews that already exist
        results = db.execute("SELECT users.username, comment, rating FROM users INNER JOIN reviews ON users.user_id = reviews.user_id WHERE book_id = :book", {"book": book})
        reviews = results.fetchall()


        return render_template("book.html", bookDetails=bookDetails, reviews=reviews)

@app.route("/api/<isbn>", methods=['GET'])
@login_required
def api_call(isbn):

    row = db.execute("SELECT title, author, year, isbn, COUNT(reviews.id) as review_count, AVG(reviews.rating) as average_score FROM books INNER JOIN reviews ON books.id = reviews.book_id WHERE isbn = :isbn GROUP BY title, author, year, isbn", {"isbn": isbn})

    # Error checking
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid ISBN"}), 422

   
    tmp = row.fetchone()
    result = dict(tmp.items())

    result['average_score'] = float('%.2f'%(result['average_score']))

    return jsonify(result)