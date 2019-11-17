from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class FacultyLoginForm(FlaskForm):
	faculty_id = StringField('Faculty-ID')
	password = PasswordField('Password')
	submit = SubmitField('Log In')