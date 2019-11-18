import pprint
import leaves
from datetime import datetime,date
import initialize

default_leaves = 15


def view_faculty_detail(id):
	#id = (int)(input('Enter id:'))
	cursor = initialize.get_cursor()
	print(cursor)

	print('id:' + id)

	# result = cursor.find({
	# 	'faculty_id': (int)(id)
	# 	})

	# print('RESULT:')
	# print(result)

	# print('PRINTNG RESULT ELEMENTS')
	# for var in result:
	# 	pprint.pprint(var)

	ls = list(cursor.find({
	 	'faculty_id': (int)(id)
	 	}))
	print(ls)
	return ls

def update_faculty_detail(id,new_name,new_alma_mater,new_education):
	# id = (int)(input('Enter id:'))

	cursor = initialize.get_cursor()
	print('++++++++++++++++++')
	print(cursor)
	print('++++++++++++++++++')
	arr = list(cursor.find({
		'faculty_id': (int)(id)
		}))

	# result = contents.find({
	# 	'faculty_id': id
	# 	})

	# arr = list(result)
	print('--------------------------------------------------')
	print(arr)
	print('--------------------------------------------------')
	faculty_id = arr[0]['faculty_id']

	# print('Update Name?Y/n')
	# c = (input())
	if new_name != 'default':
		name = new_name
	else:
		name = arr[0]['name']

	# print('Update alma_mater?Y/n')
	# c = (input())
	if new_alma_mater != 'default':
		alma_mater = new_alma_mater
	else:
		alma_mater = arr[0]['alma_mater']
		
	# print('Update education?Y/n')
	# c = (input())
	if new_education != 'default':
		education = new_education
	else:
		education = arr[0]['education']
		
	# print('Update dept_name?Y/n')
	# c = (input())
	# if c=='Y':
	# 	dept_name = input('Enter dept_name:')
	# else:
	# 	dept_name = arr[0]['dept_name']			

	cursor.update_one({'faculty_id':faculty_id},{'$set': {
	'name':name,
	'alma_mater':alma_mater,
	'education':education,
	}})

	print('UPDATED DONE')


def apply_leave(contents):
	id = (int)(input('Enter id:'))

	result = contents.find({
		'faculty_id': id
		})

	arr = list(result)

	dept_name = arr[0]['dept_name']

	start_date = input('Enter start date in yyyy-mm-dd format')
	end_date = input('Enter end date  in yyyy-mm-dd format')
	reason = input('Enter reason for absence')

	s_d = date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]))
	e_d = date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10]))
	diff = e_d - s_d

	leaves_left = arr[0]['leaves_left']

	if leaves.get_current_position_name(1) == 'HOD':
		status = 'AT HOD ' + dept_name
	else:
		status = 'AT ' + leaves.get_current_position_name(1)
	print('Status: ' + status)

	if(diff.days>(leaves_left)):
		if(diff.days < leaves_left + default_leaves):
			print('Not enough leaves left in this year. Would you like to borrow leaves from next year?Y/n')
			c = input()
			if c=='Y':
				if leaves_left + default_leaves > 0:
					if leaves_left >= 0:
						borrowed_leaves = diff.days - leaves_left	
					else:
						borrowed_leaves = diff.days
					

					# if arr[0]['position'] == 'HOD':
					# 	status = 'AT DIRECTOR'
					# elif arr[0]['position'] == 'DFA':
					# 	status = 'AT DIRECTOR'
					# else:
					# 	status = 'AT HOD ' + dept_name
					
					# if leaves.get_current_position_name(1) == 'HOD':
					# 	status = 'AT HOD ' + dept_name
					# else:
					# 	status = 'AT ' + leaves.get_current_position_name(1)
					leave_id = leaves.insert_leaves_table(start_date,end_date,reason,id,status,borrowed_leaves)

					if leave_id == -1:
						print('Your previous application has not been approved. You cannot apply for a new leave application right now')
					else:
						print('Leave application has been sent to HOD for approval. Leave ID:' + str(leave_id))
						print(str(borrowed_leaves) + ' leaves have been borrowed')
						contents.update_one({'faculty_id':id},{'$set':{
							'leave_id':leave_id
							}})

				else:
					print('You have exhausted next year leaves')

		else:
			print('You do not have enough leaves to borrow from next year')					


	else:
		# if arr[0]['position'] == 'HOD':
		# 	status = 'AT DIRECTOR'
		# elif arr[0]['position'] == 'DFA':
		# 	status = 'AT DIRECTOR'
		# else:
		# 	status = 'AT HOD ' + dept_name


		leave_id = leaves.insert_leaves_table(start_date,end_date,reason,id,status)

		if leave_id == -1:
			print('Your previous application has not been approved. You cannot apply for a new leave application right now')
		else:
			print('Leave application has been sent to HOD for approval. Leave ID:' + str(leave_id))
			contents.update_one({'faculty_id':id},{'$set':{
				'leave_id':leave_id
				}})


	
def assign_leave_id(faculty_id,leave_id):
	cursor = initialize.get_cursor()
	cursor.update_one({'faculty_id':(int)(faculty_id)},{'$set': {
	'leave_id':(int)(leave_id)
	}})



def check_leave_status(id):
	# id = (int)(input('Enter id:'))

	# result = contents.find({
	# 	'faculty_id': id
	# 	})

	cursor = initialize.get_cursor()

	arr = list(cursor.find({
		'faculty_id': (int)(id)
		}))

	print(arr)

	return leaves.leave_status(arr[0]['leave_id'])

	


if __name__ == "__main__":
	def faculty_func(contents):
		global_var = contents
		print('global_var initialized')
		print(global_var)
		print('faculty access granted')
		print('Enter 1 to view faculty detail')
		print('Enter 2 to update details')
		print('Enter 3 to apply for leave')
		print('Enter 4 to check leave status')

		i = (int)(input())

		if i==1:
			view_faculty_detail(contents)
		elif i==2:
			update_faculty_detail(contents)
		elif i==3:
			apply_leave(contents)
		elif i==4:
			check_leave_status(contents)