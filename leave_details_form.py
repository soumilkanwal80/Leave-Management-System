from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class LeaveDetailsForm(FlaskForm):
	comment = StringField('Comment')
	submit = SubmitField('Submit')