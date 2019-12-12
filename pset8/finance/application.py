import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
#    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

    # Get the logged in user's id
    user_id = int(session.get("user_id"))

    # Query the db for the user's cash amount
    cash_onhand = db.execute("SELECT cash FROM users WHERE id = :id",
                             id=user_id)

    # Get the actual number value for cash
    cash_onhand = cash_onhand[0].get("cash")

    # Get the user's stocks and the sum of shares of each stock
    stock_info = db.execute("""SELECT stock, SUM(shares) shares FROM history
                            WHERE user_id = :user_id GROUP BY stock""",
                            user_id=user_id)

    # Set up the total cash incl. onhand+stocks
    total_cash = cash_onhand

    # Iterate through the dicts in list stock_info
    for i in range(len(stock_info)):

        # Use lookup to get stock info, add the price to the dict
        stock = lookup(stock_info[i].get("stock"))
        stock_info[i].update({'price': stock["price"]})

        # Find the total cash value of stocks * number of shares, add to dict
        total_value = stock_info[i]['price'] * stock_info[i]['shares']
        stock_info[i].update({'total': total_value})

        # Add the cash_onhand found earlier + total_value above for new total
        total_cash += total_value

    return render_template("index.html", stock_info=stock_info,
                           cash_onhand=cash_onhand, total_cash=total_cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "POST":
        # Get the symbol and use it to lookup the stock info
        symbol = request.form.get("symbol")
        stock_info = lookup(symbol)
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("valid ints only please", 400)

        if not stock_info:
            return apology("please enter a valid stock symbol", 400)
        elif shares < 1:
            return apology("please enter a positive number of shares", 400)

        # Get the price of the stock as a variable, and of price * shares
        stock_price = float(stock_info["price"])
        total_price = stock_price * shares

        # Get amount of cash user has in their account
        cash_onhand = db.execute("SELECT cash FROM users WHERE id = :id",
                                 id=int(session.get("user_id")))

        cash_onhand = cash_onhand[0].get("cash")

        # Compare total purchase price to cash in user account
        new_cash_total = cash_onhand - total_price

        # You can't go negative in cash
        if new_cash_total < 0:
            return apology("you don't have enough cash for this transaction")

        # If user has enough cash, update their total cash & the transaction table
        else:
            db.execute("UPDATE users SET cash = :cash WHERE id = :id",
                       cash=new_cash_total, id=session.get("user_id"))
            db.execute("""INSERT INTO history (user_id,stock,cost,shares,total)
                        VALUES (:user_id,:stock,:cost,:shares,:total)""",
                       user_id=session.get("user_id"), stock=symbol,
                       cost=stock_price, shares=shares, total=total_price)
            return render_template("bought.html", symbol=symbol,
                                   stock_price=stock_price,
                                   shares=shares, total_price=total_price,
                                   new_cash_total=new_cash_total)

    return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Pull the username from the request
    username = request.args.get("username")

    # Get the rows from the users db
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                      username=username)

    if len(username) < 1:
        return jsonify(True)
    elif len(rows) < 1:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():

    # Get user id
    user_id = int(session.get("user_id"))

    # Get all transactions for user
    stock_info = db.execute("SELECT * FROM history WHERE user_id = :user_id",
                            user_id=user_id)

    return render_template("history.html", stock_info=stock_info)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    if request.method == "POST":

        # Get the symbol from the user
        if not request.form.get("symbol"):
            return apology("please enter a stock symbol", 400)

        symbol = request.form.get("symbol")

        quote = lookup(symbol)

        if not quote:
            return apology("please enter a valid stock symbol", 400)

        return render_template("quoted.html", quote=quote)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password + confirmation submitted & match
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must confirm password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username isn't already in database
        if len(rows) != 0:
            return apology("username already taken, please select another")

        # Hash the pass
        hashed_pass = generate_password_hash(request.form.get("password"))

        # Insert username and hashed password into the DB
        db.execute("INSERT INTO users (username,hash) VALUES (:username, :hash)",
                   username=request.form.get("username"), hash=hashed_pass)

        # Redirect home
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/reset", methods=["GET", "POST"])
def reset():

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide current password", 403)
        elif not request.form.get("new_pass"):
            return apology("must provide new password", 403)
        elif not request.form.get("new_conf"):
            return apology("must confirm new password", 403)
        elif request.form.get("new_pass") != request.form.get("new_conf"):
            return apology("new password and confirmation must match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # If successful verification, hash new password
        new_hashed_pass = generate_password_hash(request.form.get("new_pass"))

        # Update user with new hash
        db.execute("UPDATE users SET hash = :hash where username = :username",
                   username=request.form.get("username"), hash=new_hashed_pass)

        # Logout & redirect
        session.clear()

        return redirect("/login")

    else:
        return render_template("reset.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    # Get the logged in user's id
    user_id = int(session.get("user_id"))

    # Get user's available stock symbols
    user_stocks = db.execute("""SELECT stock, SUM(shares) shares FROM history
                             WHERE user_id = :user_id GROUP BY stock""",
                             user_id=user_id)

    if request.method == "POST":

        try:
            shares_sell = int(request.form.get("shares"))
        except:
            return apology("valid ints only please", 400)

        # Check for missing input
        if not request.form.get("symbol"):
            return apology("please select a stock to sell", 400)
        elif not shares_sell or shares_sell < 1:
            return apology("please select a number of shares to sell", 400)

        # Set up variables for later
        symbol = request.form.get("symbol")

        price = float(lookup(symbol)["price"])
        total_value = price * shares_sell

        shares_owned = db.execute("""SELECT SUM(shares) shares FROM history
                                  WHERE user_id = :user_id AND stock = :stock""",
                                  user_id=user_id, stock=symbol)

        # Calculate how many shares the user will have left
        shares_left = int(shares_owned[0]["shares"] - shares_sell)
        if shares_left < 0:
            return apology("can't sell more shares than owned", 400)

        # If user has enough shares, update their total cash & the transaction table
        else:
            # Get user's cash amount
            cash_onhand = db.execute("SELECT cash FROM users WHERE id = :id",
                                     id=int(session.get("user_id")))
            cash_onhand = cash_onhand[0].get("cash")

            # Get the new total after sale
            new_cash_total = cash_onhand + total_value

            db.execute("UPDATE users SET cash = :cash WHERE id = :id",
                       cash=new_cash_total, id=session.get("user_id"))
            db.execute("""INSERT INTO history (user_id,stock,cost,shares,total)
                       VALUES (:user_id,:stock,:cost,:shares,:total)""",
                       user_id=user_id, stock=symbol,
                       cost=price, shares=-shares_sell, total=total_value)

            return render_template("sold.html", symbol=symbol,
                                   price=price,
                                   shares_sell=shares_sell, total_value=total_value,
                                   new_cash_total=new_cash_total)

    return render_template("sell.html", user_stocks=user_stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
