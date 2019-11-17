from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class FacultyUpdateForm(FlaskForm):
	name = StringField('Name',default = 'default')
	alma_mater = StringField('Alma_Mater',default = 'default')
	education = StringField('Education',default = 'default')
	update = SubmitField('Update')