from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField


class ChangePasswordForm(FlaskForm):
	current_password = PasswordField('Enter current password')
	new_password = PasswordField('Enter new password')
	confirm_new_password = PasswordField('Confirm new password')
	submit = SubmitField('Apply Changes')