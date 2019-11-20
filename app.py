from flask import Flask, render_template, flash, redirect, url_for, request
from faculty_login_form import FacultyLoginForm
import initialize as init
import faculty_logic
import pprint
from faculty_update_form import FacultyUpdateForm
from admin_login_form import AdminLoginForm
from new_faculty_form import NewFacultyForm
import admin_logic
from delete_faculty_form import DeleteFacultyForm
from change_position_form import ChangePositionForm
from hod_login_form import HODLoginForm
from dean_login_form import DeanLoginForm
from director_login_form import DirectorLoginForm
from leave_details_form  import LeaveDetailsForm
from change_password_form import ChangePasswordForm
import os
import re
# from flask import Flask, request, url_for, render_template, redirect, flash
from leaves import initialize, insert_leaves_table, getLeavesWithStatus, getBorrowedLeaves, update_leave_table, delete_from_borrowed, insert_trail, getLeaveDataWithLeaveId, add_comments, drop_faculty_leaves_order_table, update_faculty_leaves_order_table, get_faculty_leaves_order_table_size, get_current_position_name, get_current_position_num
from leaves import get_trail
from flask_wtf import  FlaskForm
from wtforms import StringField, DateField, SubmitField, TextField
from wtforms.validators import DataRequired, Length
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
initialize()

s_d = 1
e_d = 1
rsn = 1
stus = 1

class LeaveApplicationForm(FlaskForm):
    start_date = DateField('Start Date', [DataRequired()], format = '%Y-%m-%d')
    end_date = DateField('End Date', [DataRequired()], format = '%Y-%m-%d')
    reason = TextField('Reason')
    submit = SubmitField('Submit')





@app.route('/applyLeave/<int:faculty_id>', methods = ('GET', 'POST'))
def applyLeave(faculty_id):
    leaveApplication = LeaveApplicationForm()
    if (not leaveApplication.validate_on_submit()):
    	print('Invalid Form')
    	return render_template('leaveApplication.html', form = leaveApplication, faculty_id = faculty_id)

    mongo_cursor = init.get_cursor()
    details = list(mongo_cursor.find({
    	'faculty_id': (int)(faculty_id)
    	}))

    if len(details) == 0:
    	return render_template('error_template.html', error = 'Faculty-ID:' + faculty_id + ' does not exist in database')

    dept_name = details[0]['dept_name']			  
    
    if get_current_position_name(1) == 'HOD':
        status = 'AT HOD ' + dept_name
    else:
        status = 'AT ' + get_current_position_name(1)
    print('Status: ' + status)

    if faculty_logic.get_faculty_type(faculty_id) == False:
        status = 'AT DIRECTOR'

    start_date = leaveApplication.start_date.data
    end_date = leaveApplication.end_date.data

    leaves_left = faculty_logic.getRemainingLeaves(faculty_id)
    diff_date = end_date - start_date
    days_applied = diff_date.days
    default_leaves = 15

    if(days_applied > leaves_left):
        if(days_applied < leaves_left + default_leaves):
            global s_d, e_d, rsn, stus
            s_d = start_date
            e_d = end_date
            rsn = leaveApplication.reason.data
            stus = status
            return redirect(url_for('borrowLeaves', faculty_id = faculty_id, days_applied = days_applied, leaves_left = leaves_left))

    x = insert_leaves_table(leaveApplication.start_date.data, leaveApplication.end_date.data, leaveApplication.reason.data, faculty_id, status)
    print(x)
    if x != -1:
   		faculty_logic.assign_leave_id(faculty_id, x)
    else:
        return redirect(url_for('leave_exists'))
    
    return redirect(url_for('home'))

@app.route('/not_enough_leaves_left')
def not_enough_leaves_left():
    return 'Not Enough Leaves Left'

@app.route('/leave_already_applied')
def leave_exists():
    return 'Leave Already Exists'

@app.route('/borrow_leave/<faculty_id>/<days_applied>/<leaves_left>', methods = ["GET", "POST"])
def borrowLeaves(faculty_id, days_applied, leaves_left):
    leaves_left = int(leaves_left)
    days_applied = int(days_applied)
    borrowed_left = leaves_left + 15
    if(borrowed_left > 15):
        borrowed_left = 15
    if(leaves_left < 0):
        leaves_left = 0
    param = 0
    if(request.method == "POST"):
        choice = request.values.get('choice')
        if(choice == "yes"):
            if leaves_left + 15 > 0:
                if leaves_left >= 0:
                    borrowed_leaves = days_applied - leaves_left	
                else:
                    borrowed_leaves = days_applied
            else:
                return redirect(url_for('not_enough_leaves_left'))

            x = insert_leaves_table(s_d, e_d, rsn, faculty_id, stus, borrowed_leaves)
            if x != -1:
                faculty_logic.assign_leave_id(faculty_id, x)
                return redirect(url_for('home'))
            else:
                return redirect(url_for('leave_exists'))
        else:
            return redirect(url_for('applyLeave', faculty_id = faculty_id))

    return render_template('borrowLeaves.html', leaves_left = leaves_left, borrowed_left =  borrowed_left, param = param)


@app.route('/viewLeaves/<approver_name>/<position>', defaults =  {'department':None})
@app.route('/viewLeaves/<approver_name>/<position>/<department>', methods = ["GET", "POST"])
def viewLeaves(approver_name, position, department = None):
    check = False

    max_position_num = get_faculty_leaves_order_table_size()
    position_num = get_current_position_num(position)


    if position == 'HOD' and department is not None:
        status = 'AT ' + str(position) + ' ' + str(department)
    else:
        status = 'AT ' + str(position)

    if (request.values.get('approve')is not None):
        leave_id_approved = int(request.values.get('approve'))
        row = getLeaveDataWithLeaveId(leave_id_approved)
        if faculty_logic.get_faculty_type(row[6]) == True:
            if(position_num == max_position_num):
                update_leave_table(
                    'APPROVED AT ' + position, leave_id_approved)
                start_date = row[1]
                end_date = row[2]
                diff = end_date - start_date
                faculty_logic.update_leaves(row[6], diff.days)
                delete_from_borrowed(leave_id_approved)
            
            else:
                new_position = get_current_position_name(position_num + 1)
                if new_position == 'HOD':
                    new_position = new_position + ' ' + faculty_logic.get_dept_name(row[6])
                update_leave_table('AT ' + new_position, leave_id_approved)
        else:
            update_leave_table(
                'APPROVED AT DIRECTOR', leave_id_approved)
            start_date = row[1]
            end_date = row[2]
            diff = end_date - start_date
            faculty_logic.update_leaves(row[6], diff.days)
            delete_from_borrowed(leave_id_approved)

        # approver_position = position
        # if (position == 'HOD'):
        #     approver_position = position + ' ' + department

        insert_trail(approver_name, leave_id_approved, 'kkkk')

        # if (position == 'HOD'):
        #     # insert_leaves_table(row[1], row[2], row[3], row[6], 'AT DFA')
        #     update_leave_table('AT DFA', leave_id_approved)

        # if (position == 'DIRECTOR'or position == 'DFA'):
        #     update_leave_table(
        #         'APPROVED AT ' + position, leave_id_approved)
        #     start_date = row[1]
        #     end_date = row[2]
        #     # s_d = date(int(start_date[0:4]), int(start_date[5:7]), int(start_date[8:10]))
        #     # e_d = date(int(end_date[0:4]), int(end_date[5:7]), int(end_date[8:10]))
        #     diff = end_date - start_date
        #     # list_leaves.append([row[6], diff.days])
        #     delete_from_borrowed(leave_id_approved)

    elif (request.values.get('reject')is not None):
        leave_id_rejected = int(request.values.get('reject'))
        update_leave_table('REJECTED ' + status, 
                    leave_id_rejected)
        delete_from_borrowed(leave_id_rejected)
    else:
        c_regex = re.compile(r'c(\d)+')
        comment = None
        leave_id_comment = None
        val = request.values
        if(val is not None):
            
            for key in val:
                k = c_regex.match(key)
                if(k is not None):
                    leave_id_comment = key[1:]
                if(key == 'textbox'):
                    comment = val[key]
            if(comment is None and leave_id_comment is None):
                print('why')
            elif(comment is not '' and leave_id_comment is not ''):
                check = True
                comment = position + ': ' + comment + '\n'
                add_comments(leave_id_comment, comment)


    allLeaves = getLeavesWithStatus(status)
    updatedLeaves = []
    for row in allLeaves:
        borrowedLeaves = getBorrowedLeaves(row[0])
        x = list(row)
        if(borrowedLeaves != []):
            borrowedLeaves = borrowedLeaves[0]
            x.append(borrowedLeaves[1])
        else:
            x.append('0')
        updatedLeaves.append(x)
    updatedLeaves = tuple(updatedLeaves)
    if check is False:
        return render_template('displayLeaves.html', data=updatedLeaves, approver_name = approver_name, position = position, department = None)
    else:
        return redirect(request.path, code = 302)


@app.route('/view_leave_status/<faculty_id>', methods = ['GET','POST'])
def view_leave_status(faculty_id):
	leave_details = faculty_logic.check_leave_status(faculty_id)

	if len(leave_details) == 0:
		return render_template('error_template.html', error = 'No leave application')
	form = LeaveDetailsForm()
	if form.validate_on_submit():
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'faculty_id': (int)(faculty_id)
			}))

		name = details[0]['name']
		print('Leave details form validated')
		add_comments((int)(leave_details['leave_id']),name + ': ' + form.comment.data + '\n')
		new_details = faculty_logic.check_leave_status(faculty_id)
		form.comment.data = ''
		###############################
		return render_template('leave_details.html', leave_details = new_details, form = form, faculty_id = faculty_id)
		###############################
	return render_template('leave_details.html', leave_details = leave_details, form = form, faculty_id = faculty_id)


@app.route('/admin/change_route', methods = ["POST", "GET"])
def changeRoute():
    return render_template('new_route.html')

@app.route('/admin/change_route/submit', methods = ["POST", "GET"])
def updateRoute():
    drop_faculty_leaves_order_table()
    maxi = 0;
    for i in range(1, 10):
        person = request.values.get("text_" + str(i))
        if person is '':
            maxi = i
            break
        update_faculty_leaves_order_table(person)

            
    return redirect(url_for('admin'))


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

# @app.route('/faculty_options')
@app.route('/faculty_options/<faculty_id>')
def faculty_options(faculty_id, methods = ['GET', 'POST']):
	return render_template('faculty_options.html', faculty_id = faculty_id)

@app.route('/profile/<faculty_id>')
def profile(faculty_id):
	print('faculty_id:' + str(type(faculty_id)))
	# print('contents:' + str(type(contents)))
	print(faculty_id)
	# print(contents)

	details = faculty_logic.view_faculty_detail(faculty_id)

	if len(details) == 0:
		return render_template('error_template.html', error = 'Faculty-ID:' + form.faculty_id.form + 'is not present in database')
	print(details)
	for var in details:
		print('INSIDE APP.PY')
		pprint.pprint(details)
	return render_template('profile.html',arr = details)



@app.route('/update/<faculty_id>',methods = ['GET','POST'])
def update(faculty_id):
	details = faculty_logic.view_faculty_detail(faculty_id)

	if len(details) == 0:
		return render_template('error_template.html', error = 'Faculty-ID:' + form.faculty_id.form + 'is not present in database')
	
	form = FacultyUpdateForm()
	if form.validate_on_submit():
		flash(f'Details updated','success')


		faculty_logic.update_faculty_detail(faculty_id,form.name.data,form.alma_mater.data,form.education.data)
		return render_template('faculty_options.html',faculty_id = faculty_id)

	return render_template('update.html',faculty_id = details[0]['faculty_id'],name = details[0]['name']
		,alma_mater = details[0]['alma_mater'],education = details[0]['education'],form = form)	


	
@app.route('/faculty',methods=['GET','POST'])
def faculty():
	form = FacultyLoginForm()
	if form.validate_on_submit():
		flash(f'Account created for {form.faculty_id.data}','success')
		print('faculty_id:'+ form.faculty_id.data + 'password:'+form.password.data)
		# contents = initialize.get_cursor()
		details = faculty_logic.view_faculty_detail(form.faculty_id.data)

		if len(details) == 0:
			return render_template('error_template.html', error = 'Faculty-ID:' + form.faculty_id.data + ' is not in database')

		if details[0]['password'] == form.password.data:
			return render_template('faculty_options.html',faculty_id = form.faculty_id.data, dept_name = details[0]['dept_name'], 
				position = details[0]['position'], name = details[0]['name'])	

		else:
			return render_template('error_template.html', error = 'Password for Faculty-ID:' + str(details[0]['faculty_id']) + ' is incorrect')	
		

	return render_template('faculty.html', form = form)	


@app.route('/admin',methods = ['GET','POST'])
def admin():
	form = AdminLoginForm()
	if form.validate_on_submit():
		flash(f'Admin Login Succesful')
		return render_template('admin_options.html')
	return render_template('admin.html', form = form)

@app.route('/admin_options')	
def admin_options():
	return render_template('admin_options.html')

@app.route('/new_faculty',methods = ['GET','POST'])
def new_faculty():
	form = NewFacultyForm()
	if form.validate_on_submit():
		print("Form validate_on_submit")
		admin_logic.add_faculty_mongo(form.name.data,form.alma_mater.data,form.education.data,form.dept_name.data,form.position.data)
		return render_template('admin_options.html')
	return render_template('new_faculty.html',form = form)


@app.route('/view_all_faculty')	
def view_all_faculty():
	arr = admin_logic.view_faculty_mongo()
	if len(arr) == 0:
		return render_template('error_template.html', error = 'No Faculty has been added yet')
	return render_template('view_all_faculty.html', arr = arr)


@app.route('/delete_faculty', methods = ['GET','POST'])
def delete_faculty():
	form = DeleteFacultyForm()
	if form.validate_on_submit():
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'faculty_id':(int)(form.faculty_id.data)
			}))

		if len(details) == 0:
			return render_template('error_template.html', error = 'Faculty-ID:' + form.faculty_id.data + ' is not present in database')

		if details[0]['position'] == 'HOD' or details[0]['position'] == 'DFA' or details[0]['position'] == 'DSA' or details[0]['position'] == 'DIRECTOR':
			return (render_template('error_template.html',
				error = 'Cannot delete HOD account. Assign someone else as ' + details[0]['position'] + '( or add a new ' 
				 + details[0]['position'] +') before deleting this account'))
		
		print('Deletion Form validated')
		admin_logic.delete_faculty_mongo(form.faculty_id.data)
		return render_template('admin_options.html')

	return render_template('delete_faculty.html',form = form)

@app.route('/change_position', methods = ['GET','POST'])
def change_position():
	form = ChangePositionForm()
	if form.validate_on_submit():
		print('Change position validated')
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'faculty_id':(int)(form.faculty_id.data)
			}))

		if len(details) == 0:
			return render_template('error_template.html', error = 'Faculty-ID:' + form.faculty_id.data + 'does not exist in database')

		if form.dept_name.data == 'None' and form.position.data == 'HOD':
			return render_template('error_template.html', error = 'Please specify department while changing HOD')

		if form.dept_name.data != details[0]['dept_name'] and form.position.data == 'HOD':	
			return render_template('error_template.html', error = 'Faculty being made HOD should be of the same department\n' + 
				'current department of faculty:' + details[0]['dept_name'] +
				'\n department being assigned:' + form.dept_name.data)
		
		admin_logic.change_faculty_position(form.position.data,form.dept_name.data,form.faculty_id.data)		

	return render_template('change_position.html',form = form)


@app.route('/hod_login',methods = ['GET','POST'])
def hod_login():
	form = HODLoginForm()	
	if form.validate_on_submit():
		print('Form validated succesfully')
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'position':'HOD',
			'dept_name': form.dept_name.data
			}))

		if len(details) == 0:
			return render_template('error_template.html', error = 'There is no HOD for ' + form.dept_name.data + ' department')

		print(details)
		return redirect(url_for('viewLeaves',approver_name = details[0]['name'], position = 'HOD', department = details[0]['dept_name'])) 
		# viewLeaves(approver_name = details[0]['name'], position = 'HOD', department = details[0]['dept_name'])


	return render_template('hod_login.html', form = form)

@app.route('/dean_login',methods = ['GET','POST'])
def dean_login():
	form = DeanLoginForm()
	if form.validate_on_submit():
		print('Dean Login Succesful')
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'position':'D' + form.area.data
			}))

		if len(details) == 0:
			return render_template('error_template.html', error = 'There is no D' + form.area.data)
		print(details)
		return redirect(url_for('viewLeaves',approver_name = details[0]['name'], position = details[0]['position']))
	return render_template('dean_login.html',form = form)


@app.route('/director_login',methods = ['GET','POST'])
def director_login():
	form = DirectorLoginForm()
	if form.validate_on_submit():
		print('Director Login Succesful')
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'position':'Director'
			}))

		if len(details) == 0:
			return render_template('error_template.html', error = 'No Director has been appointed')
		print(details) 		
		return redirect(url_for('viewLeaves',approver_name = details[0]['name'], position = (details[0]['position']).upper()))
        

	return render_template('director_login.html', form = form)	

@app.route('/change_password/<faculty_id>', methods = ['GET', 'POST'])
def change_password(faculty_id):
	form = ChangePasswordForm()
	if form.validate_on_submit():
		print('Password change form validated')
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'faculty_id': (int)(faculty_id)
			}))

		if len(details) == 0:
			return render_template('error_template.html', error = 'Faculty-ID:' + form.faculty_id.data + 'does not exist in database')

		if details[0]['password'] == form.current_password.data and form.new_password.data == form.confirm_new_password.data:
			mongo_cursor.update_one({'faculty_id':(int)(faculty_id)},{
			'$set':{
			'password': form.new_password.data
			}
		})

		return redirect(url_for('faculty'))	

	return render_template('change_password.html', form = form, faculty_id = faculty_id)


@app.route('/view_trail')
def view_trail():
	arr = get_trail()
	return render_template('trail.html', arr = arr) 			

if __name__ == "__main__":
	app.run(debug = True)
	
