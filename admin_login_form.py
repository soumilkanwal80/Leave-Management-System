from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class AdminLoginForm(FlaskForm):
	admin_id = StringField('DB-Admin ID')
	password = PasswordField('Password')
	submit = SubmitField('Log In')