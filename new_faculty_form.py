from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class NewFacultyForm(FlaskForm):
	name = StringField('Name')
	alma_mater = StringField('Alma Mater')
	education = StringField('Education')
	dept_name = StringField('Department Name')
	position = StringField('Position',default = 'Faculty')
	submit = SubmitField('Submit')