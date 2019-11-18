import pprint
import initialize

default_leaves = 15


def add_faculty_mongo(new_name,new_alma_mater,new_education,new_dept_name,new_position):

	cursor = initialize.get_cursor()

	faculty_id = 0

	arr = list(cursor.find().sort([('faculty_id',-1)]).limit(1))

	if len(arr) == 0:
		faculty_id = 1

	else:
		faculty_id = arr[0]['faculty_id'] + 1
		
	name = new_name
	alma_mater = new_alma_mater
	education = new_education
	dept_name = new_dept_name
	leaves_left = default_leaves
	leave_id = None
	position = new_position
	password = 'password'

	faculty = {
	'faculty_id': faculty_id,
	'name': name,
	'alma_mater': alma_mater,
	'education': education,
	'dept_name': dept_name,
	'leaves_left': leaves_left,
	'leave_id': leave_id,
	'position':position,
	'password':password
	}



	result = cursor.insert_one(faculty)

	if result.acknowledged:
		print('Faculty added succesfully--ID:' + str(result.inserted_id))

		


def view_faculty_mongo():
	cursor = initialize.get_cursor()
	# faculty = cursor.find()
	# for i in faculty:
	# 	pprint.pprint(i)

	arr = list(cursor.find())

	return arr



def delete_faculty_mongo(faculty_id):
	# print('Enter id')
	# faculty_id = (int)(input())

	cursor = initialize.get_cursor()
	query = {
	'faculty_id': (int)(faculty_id),
	}

	result = cursor.find(query)
	for i in result:
		pprint.pprint(i)

	cursor.delete_one(query)


def change_faculty_position(req_position,req_dept,new_faculty_id):
	# position = input('Enter position to be modified:')

	cursor = initialize.get_cursor()

	if req_position == 'HOD':
		dept = req_dept
		# result = cursor.find({
		# 	'dept_name':dept
		# 	})
		old_hod_id = -1
		new_hod_id = (int)(new_faculty_id)

		arr = list(cursor.find({
			'dept_name':dept
			}))

		print(arr)
		for i in arr:
			if i['position'] == 'HOD':
				old_hod_id = i['faculty_id']

		print('old hod id:' + str(old_hod_id))
		print('new_hod_id:' + str(new_hod_id))		

		cursor.update_one({'faculty_id':old_hod_id},{
			'$set':{
			'position':'Faculty'
			}
		})

		cursor.update_one({'faculty_id':new_hod_id},{
			'$set':{
			'position':'HOD'
			}
		})			

# def admin_func(contents):
# 	print('admin access granted')
# 	print('Enter 1 to add new faculty')
# 	print('Enter 2 to view detailed profile')
# 	print('Enter 3 to delete faculty')
# 	print('Enter 4 to update cross-cutting faculty positions')
# 	i = (int)(input())
# 	if i==1:
# 		add_faculty_mongo(contents)
# 	elif i==2:
# 		view_faculty_mongo(contents)
# 	elif i==3:
# 		delete_faculty_mongo(contents)
# 	elif i==4:
# 		change_faculty_position(contents)