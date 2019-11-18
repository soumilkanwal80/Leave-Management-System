from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class DeanLoginForm(FlaskForm):
	dean_id = StringField('Dean-ID')
	area = StringField('Area')
	password = PasswordField('Password')
	submit = SubmitField('Log In')