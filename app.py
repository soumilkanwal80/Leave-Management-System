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
import os
import re
# from flask import Flask, request, url_for, render_template, redirect, flash
from leaves import initialize, insert_leaves_table, getLeavesWithStatus, getBorrowedLeaves, update_leave_table, delete_from_borrowed, insert_trail, getLeaveDataWithLeaveId, add_comments, drop_faculty_leaves_order_table, update_faculty_leaves_order_table, get_faculty_leaves_order_table_size, get_current_position_name, get_current_position_num
from flask_wtf import  FlaskForm
from wtforms import StringField, DateField, SubmitField, TextField
from wtforms.validators import DataRequired, Length
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
initialize()



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
    
    if get_current_position_name(1) == 'HOD':
        status = 'AT HOD ' + 'CSE'
    else:
        status = 'AT ' + get_current_position_name(1)
    print('Status: ' + status)

    if faculty_logic.get_faculty_type(faculty_id) == False:
        status = 'AT DIRECTOR'

    x = insert_leaves_table(leaveApplication.start_date.data, leaveApplication.end_date.data, leaveApplication.reason.data, faculty_id, status)
    print(x)
    if x != -1:
   		faculty_logic.assign_leave_id(faculty_id, x)
    return redirect(url_for('home'))


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
                # list_leaves.append([row[6], diff.days])
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
            # list_leaves.append([row[6], diff.days])
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
	form = LeaveDetailsForm()
	if form.validate_on_submit():
		mongo_cursor = init.get_cursor()
		details = list(mongo_cursor.find({
			'faculty_id': (int)(faculty_id)
			}))

		name = details[0]['name']
		print('Leave details form validated')
		add_comments((int)(leave_details['leave_id']),name + ': ' + form.comment.data)
		new_details = faculty_logic.check_leave_status(faculty_id)
		form.comment.data = ''
		###############################
		return render_template('leave_details.html', leave_details = new_details, form = form)
		###############################
	return render_template('leave_details.html', leave_details = leave_details, form = form)


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

@app.route('/faculty_options')
def faculty_options():
	render_template('faculty_options.html')

@app.route('/profile/<faculty_id>')
def profile(faculty_id):
	print('faculty_id:' + str(type(faculty_id)))
	# print('contents:' + str(type(contents)))
	print(faculty_id)
	# print(contents)

	details = faculty_logic.view_faculty_detail(faculty_id)

	if len(details) == 0:
		return render_template('error_faculty_id.html')
	print(details)
	for var in details:
		print('INSIDE APP.PY')
		pprint.pprint(details)
	return render_template('profile.html',arr = details)



@app.route('/update/<faculty_id>',methods = ['GET','POST'])
def update(faculty_id):
	details = faculty_logic.view_faculty_detail(faculty_id)

	if len(details) == 0:
		return render_template('error_faculty_id.html')
	
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

		if details[0]['password'] == form.password.data:
			return render_template('faculty_options.html',faculty_id = form.faculty_id.data, dept_name = details[0]['dept_name'])	

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
	return render_template('view_all_faculty.html', arr = arr)


@app.route('/delete_faculty', methods = ['GET','POST'])
def delete_faculty():
	form = DeleteFacultyForm()
	if form.validate_on_submit():
		print('Deletion Form validated')
		admin_logic.delete_faculty_mongo(form.faculty_id.data)
		return render_template('admin_options.html')

	return render_template('delete_faculty.html',form = form)

@app.route('/change_position', methods = ['GET','POST'])
def change_position():
	form = ChangePositionForm()
	if form.validate_on_submit():
		print('Change position validated')
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
		print(details) 		
		return redirect(url_for('viewLeaves',approver_name = details[0]['name'], position = (details[0]['position']).upper()))
        

	return render_template('director_login.html', form = form)	

if __name__ == "__main__":
	app.run(debug = True)
	
