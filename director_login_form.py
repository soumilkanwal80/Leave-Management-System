from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class DirectorLoginForm(FlaskForm):
	director_id = StringField('Director-ID')
	password = PasswordField('Password')
	submit = SubmitField('Log In')