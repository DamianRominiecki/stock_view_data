from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed
from .models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    email = EmailField("Email:", validators=[InputRequired(message="A email is required!")])
    password = PasswordField("Password:", validators=[InputRequired(message="A password is required!")])
    remember = BooleanField('Remember Me')
    submit = SubmitField("Login", validators=[InputRequired()])

class SignupForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(message="A username is required!")])
    email = EmailField('Email:', validators=[InputRequired(message="A email is required!")])
    password = PasswordField('Password:', validators=[InputRequired(message="Please enter a password!")])
    confirm_password = PasswordField('Repeat Password:', validators=[InputRequired(message="Repeat a password!"), EqualTo('password')])
    submit = SubmitField("Submit", validators=[InputRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please use a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please use a different one.')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please use a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please use a different one.')

class RequestResetForm(FlaskForm):
    email = StringField("Email:", validators=[InputRequired(message="A email is required!")])
    submit = SubmitField("Reset password", validators=[InputRequired()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")