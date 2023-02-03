from flask import Blueprint, redirect, render_template, flash, request, session, url_for
from flask_login import login_required, logout_user, current_user, login_user
from .forms import LoginForm, SignupForm, RequestResetForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, app, mail
from .models import User
from flask_mail import Message

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user_check = db.session.query(User).filter(User.email==form.email.data).first()
        if user_check:
            if check_password_hash(user_check.password, form.password.data):
                login_user(user_check, remember=True)
                flash("Login Successful!")
                return redirect(url_for('views.home'))
            else:
                flash('Login Unsuccessful. Please check email and password.')

        if "next" in session and session["next"]:
            return redirect(session["next"])
    session["next"] = request.args.get("next")
    return render_template("login.html", form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!')
        return redirect(url_for('auth_bp.login'))
    return render_template("signup.html", form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", sender="noreply@demo.com", recipients=[user.email])
    msg.body = f"""To reset your password visit following link: {url_for('auth_bp.reset_token', token=token, _external=True)}
    If you didn't make this request then ignore this email."""
    mail.send(msg)

@auth_bp.route('/reset_password', methods=["POST", "GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions.", "info")
        redirect(url_for("auth_bp.login"))
    return render_template("reset_request.html", form=form, title="Reset Password")

@auth_bp.route('/reset_password/<token>', methods=["POST", "GET"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('auth_bp.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been update! You are now able to log in!')
        return redirect(url_for('auth_bp.login'))
    return render_template("reset_token.html", form=form, title="Reset Password")