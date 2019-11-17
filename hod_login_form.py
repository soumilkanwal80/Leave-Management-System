from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class HODLoginForm(FlaskForm):
	hod_id = StringField('HOD-ID')
	password = PasswordField('Password')
	submit = SubmitField('Log In')