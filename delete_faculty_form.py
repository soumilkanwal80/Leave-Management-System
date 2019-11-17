from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class DeleteFacultyForm(FlaskForm):
	faculty_id = StringField('Faculty-ID')
	submit = SubmitField('Delete')