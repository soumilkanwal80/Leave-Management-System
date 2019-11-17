from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class ChangePositionForm(FlaskForm):
	position = StringField('Position')
	dept_name = StringField('Department',default = 'None')
	faculty_id = StringField('Faculty-ID')
	submit = SubmitField('Apply Changes')