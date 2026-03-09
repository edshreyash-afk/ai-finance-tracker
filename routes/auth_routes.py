from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user, login_required, fresh_login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from models import db, User
from functools import wraps
import secrets
import time

auth = Blueprint("auth", __name__, url_prefix="/auth")

# WTForms for validation & CSRF
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Enter a valid email')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password too short')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message='Username 3-20 chars')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Invalid email')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password too short')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords don't match")
    ])
    submit = SubmitField('Create Account')

# Rate limiting decorator (simple)
from collections import defaultdict
login_attempts = defaultdict(list)

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        now = time.time()  
        attempts = login_attempts[ip]
        attempts[:] = [t for t in attempts if now - t < 900]  # 15 min window
        if len(attempts) > 5:
            flash('Too many login attempts. Try again in 15 minutes.', 'error')
            return render_template('login.html', form=LoginForm())
        attempts.append(now)
        return f(*args, **kwargs)
    return decorated_function

@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered!", "error")
            return render_template("register.html", form=form)
        
        hashed_password = generate_password_hash(form.password.data, method='scrypt')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for('auth.login'))
    
    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
@rate_limit
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next', url_for('dashboard.index'))
            flash("Welcome back!", "success")
            return redirect(next_page)
        flash("Invalid email or password!", "error")
    
    return render_template("login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("auth.login"))

@auth.route("/forgot_password")
def forgot_password():
    flash("Password reset links coming soon!", "info")
    return redirect(url_for("auth.login"))
