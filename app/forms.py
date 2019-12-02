"""
A new module to store my web form classes
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    # the Data Required validator simply checks that the field is not empty
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    # Methods that follow the pattern validate_xxx will be used by WTForms as custom validators
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email")


class EditProfileForm(FlaskForm):
    """
    A form that allows the user to change their username, and About Me section.
    We've allocated 140 characters for the about me section in the database, so we use Length() validator to ensure
    that this is the maximum.
    """
    username: StringField = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """
        Validates that a chosen new username does not already exist in the database.
        If it does, prompt user to choose a different new username

        This is a custom validation method with an overloaded constructor that accepts the original username
        as an argument.

        The username is saved as an instance variable and checked in the validate_username method.
        """
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username')


class PostForm(FlaskForm):
    post = TextAreaField("Say something", validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField("Submit")
