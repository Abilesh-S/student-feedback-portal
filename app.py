from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user

from models import db, Feedback
from auth import auth

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///feedback.db"
app.config["SECRET_KEY"] = "supersecret"

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

app.register_blueprint(auth)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        course = request.form.get("course")
        rating = request.form.get("rating")
        comments = request.form.get("comments")

        if course and rating:
            feedback = Feedback(course=course, rating=int(rating), comments=comments, user_id=current_user.id)
            db.session.add(feedback)
            db.session.commit()
            return redirect(url_for("thanks"))
    return render_template("index.html")


@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


@app.route("/admin")
@login_required
def admin():
    if current_user.email != "admin@example.com":  # only admin sees all
        return "Unauthorized", 403
    feedbacks = Feedback.query.all()
    return render_template("admin.html", feedbacks=feedbacks)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
