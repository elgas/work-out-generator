import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/get_workouts")
def get_workouts():
    workouts = mongo.db.workouts.find()
    return render_template("workouts.html", workouts=workouts)

# Code from CodeInstitute Python tutorials
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checking if username already exists in our database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already in use")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # Puting the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!!")
    return render_template("register.html")


@app.route("/add_workout", methods=["GET", "POST"])
def add_workout():
    if request.method == "POST":
        workout = {
            "workout_name": request.form.get("workout_name"),
            "workout_description": request.form.get("workout_description"),
            "workout_duration_mins": request.form.get("workout_duration_mins"),
            "created_by": session["user"]
            }
        mongo.db.workouts.insert_one(workout)
        flash("Work-out Successfully Added")
        return redirect(url_for("get_workouts"))

    categories = mongo.db.workouts.find().sort("workout_name", 1)
    return render_template("add_workout.html", categories=categories)



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), 
             port=int(os.environ.get("PORT")),
             debug=True)
