import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    # Create variables for each request field

    username = request.form.get('name')
    checkbox = request.form.get('robotcheck')
    drop_really = request.form.get('dropdownrobot1')
    drop_sorry = request.form.get('dropdownrobot2')

    # Ensure that all fields were filled in case Javascript is disabled

    if not username or not checkbox or not drop_really or not drop_sorry:
        return render_template("error.html")

    # Open survey.csv and write the response to it

    with open("survey.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow((username, checkbox, drop_really, drop_sorry))

    return redirect("/sheet")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    # Open survey.csv and pull the lines into a list as 'responses'

    with open("survey.csv", "r") as file:
        reader = csv.reader(file)
        responses = list(reader)
    return render_template("sheet.html", responses=responses)
