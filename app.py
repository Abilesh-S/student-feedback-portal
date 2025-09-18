from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from models import db, User, Feedback
from auth import bp as auth_bp
import os

app = Flask(__name__)

# Secret key for sessions (use env var in cloud, fallback local)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret")

# Database: SQLite locally, or cloud DB via DATABASE_URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register authentication routes
app.register_blueprint(auth_bp)


@app.route("/", methods=["GET", "POST"])
@login_required   # must be logged in to submit feedback
def index():
    if request.method == "POST":
        course = request.form.get("course", "").strip()
        rating = request.form.get("rating", "").strip()
        comments = request.form.get("comments", "").strip()

        if course and rating:
            fb = Feedback(course=course, rating=int(rating),
                          comments=comments, user_id=current_user.id)
            db.session.add(fb)
            db.session.commit()
            return redirect(url_for("thanks"))
    return render_template("index.html")


@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        return "Forbidden", 403
    feedbacks = Feedback.query.all()
    return render_template("admin.html", feedbacks=feedbacks)


if __name__ == "__main__":
    # Ensure DB tables are created on first run
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=True)
