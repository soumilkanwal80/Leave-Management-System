import leaves
import faculty

def view_leave_request(contents):
	id = (int)(input('Enter id:'))

	result = contents.find({
	'faculty_id': id
	})

	arr = list(result)

	leaves.approve_leave(arr[0]['name'],'HOD',arr[0]['dept_name'])



def hod_func(contents):
	print('Press 1 to view leave requests')
	i = (int)(input())
	if i==1:
		view_leave_request(contents)	

