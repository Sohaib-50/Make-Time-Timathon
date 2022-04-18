from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, login_user, logout_user
from datetime import date
from activities import get_all_topics, get_random_activity  


app = Flask(__name__) # Initialize Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "j2uHh2HjQIQgJQmOc6Ji"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

db = SQLAlchemy(app) # Initialize SQLAlchemy


class User(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class Highlight(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    highlight_date = db.Column(db.Date, nullable=False)
    planned_time = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User._id), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)

class MightDoTask(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User._id), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    task_date = db.Column(db.Date, nullable=False)

@app.route("/", methods=["GET"])
def index():
    return render_template("landing_page.html")


@app.route("/logout")
@login_required
def logout():
    # flash("You have been logged out.", "success")
    logout_user()
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # if user is already logged in, redirect to home page
    if session.get("user_id") is not None:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("login.html", title="Login")
    
    else:  # POST request
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user._id
            # flash("You have successfully logged in!", "success")
            login_user(user._id, username)
            return redirect(url_for("index"))
        else:
            flash("Incorrect username and/or password", "error")
            return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    # Make sure to properly handle GET and POST requests
    if request.method == "GET":
        return render_template("register.html", title="Register")

    elif request.method == "POST":
        # Get all the form data
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("password2")

        # check if any of the fields are empty
        if not username or not email or not password or not confirm_password:
            flash("Please fill in all the fields", "error")
            return redirect(url_for("register"))
        
        # Check if the username is already taken
        elif User.query.filter_by(username=username).first():
            flash("An account with the same username already exists!", "error")
            print("An account with the same username already exists!")
            return redirect(url_for("register"))

        # Check if the email is already taken
        elif User.query.filter_by(email=email).first():
            flash("An account with the same email already exists!", "error")
            print("An account with the same email already exists!")
            return redirect(url_for("register"))

        # Check if the passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            print("Passwords do not match!")
            return redirect(url_for("register"))

        # check if password is atleast 4 characters long
        elif len(password) < 4:
            flash("Password must be atleast 4 characters long!", "error")
            print("Password must be atleast 4 characters long!")
            return redirect(url_for("register"))
        
        # Create a new user if all checks passed
        # Hash the password
        password = generate_password_hash(password)

        # Add user to db
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        # Redirect them to home page
        # flash("You have successfully registered and logged in!", "success")
        login_user(user._id, username)
        return redirect(url_for("index"))


@app.route("/dailyhighlight", methods=["GET", "POST"])
@login_required
def dailyhighlight():
    today = date.today()

    if request.method == "GET":
        dailyhighlights = Highlight.query.filter_by(user_id=session["user_id"]).order_by(Highlight.highlight_date.desc()).all()
        todays_highlight = Highlight.query.filter_by(user_id=session["user_id"], highlight_date=today).first()  # get today's highlight if it exists
        return render_template("dailyhighlight.html", title="Daily Highlight", dailyhighlights=dailyhighlights, todays_highlight=todays_highlight, today=today)
    else:
        if request.form.get("save"):  # daily highlight saved
            # get the form data
            description = request.form.get("highlight")
            planned_time = request.form.get("time")
            if not description:
                flash("Please write a highlight", "error")
                return redirect(url_for("dailyhighlight"))

            # add the highlight to the db
            highlight = Highlight(description=description, planned_time=planned_time, highlight_date=today, user_id=session["user_id"])
            db.session.add(highlight)
            db.session.commit()
            
            flash("Highlight saved!", "success")
            return redirect(url_for("dailyhighlight"))
        elif request.form.get("update"):
            # get the form data
            description = request.form.get("highlight")
            planned_time = request.form.get("time")
            if not description:
                flash("Please write a highlight", "error")
                return redirect(url_for("dailyhighlight"))

            # update the highlight in the db
            highlight = Highlight.query.filter_by(user_id=session["user_id"], highlight_date=today).first()
            highlight.description = description
            highlight.planned_time = planned_time
            db.session.commit()
            
            flash("Highlight updated!", "success")
            return redirect(url_for("dailyhighlight"))
        
        elif request.form.get("done"):
            # get the form data
            description = request.form.get("highlight")
            planned_time = request.form.get("time")
            if not description:
                flash("Please write a highlight", "error")
                return redirect(url_for("dailyhighlight"))

            # update the highlight in the db
            highlight = Highlight.query.filter_by(user_id=session["user_id"], highlight_date=today).first()
            highlight.description = description
            highlight.planned_time = planned_time
            highlight.done = True
            db.session.commit()
            
            flash("Highlight done!", "success")
            return redirect(url_for("dailyhighlight"))


@app.route("/activities_suggestor", methods=["GET", "POST"])
@login_required
def activities_suggestor():
    if request.method == "GET":
        topics = get_all_topics()
        return render_template("activities_suggestor.html", title="Activities Suggestor", topics=topics)
    else:
        # get list of all the checked topics
        topics = request.form.getlist("topics")
        if not topics:
            flash("Please select atleast one topic", "error")
            return redirect(url_for("activities_suggestor"))

        # get an activity
        topic, activty = get_random_activity(topics)
        return render_template("activities_suggestor.html", title="Activities Suggestor", topic=topic, activity=activty)


@app.route("/mightdolist")
@login_required
def mightdolist():
    # delete all mightdotasks
    # MightDoTask.query.filter_by(user_id=session["user_id"]).delete()
    # get all the mightdotasks from the db
    mightdotasks = MightDoTask.query.where((MightDoTask.user_id == session["user_id"]) & ((MightDoTask.task_date == date.today()) | ((MightDoTask.task_date != date.today()) & (MightDoTask.done == False)))).all()
    # mightdotasks = MightDoTask.query.all()
    # print(mightdotasks)
    return render_template("mightdolist.html", title="Might Do List", tasks=mightdotasks)


@app.route("/addtask", methods=["POST"])
def addtask():
    '''API to add a might-do list task'''
    task = request.form.get("task")
    if not task:
        return jsonify({"message": "Please enter a task"}), 400
    new_task = MightDoTask(description=task, user_id=session["user_id"], task_date=date.today())
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"success": True, "task_id": new_task._id})


@app.route("/updatetask", methods=["POST"])
def updatetask():
    '''API to toggle done status of a might-do list task'''
    task_id = request.form.get("task_id")
    task = MightDoTask.query.filter_by(user_id=session["user_id"], _id=task_id).first()
    task.done = not task.done
    db.session.commit()
    print(task.done)
    return jsonify({"success": True})

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html", title="About Us")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
