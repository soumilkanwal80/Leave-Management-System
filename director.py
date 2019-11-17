import leaves

def view_leave_requests(contents):
	id = (int)(input('Enter id:'))

	result = contents.find({
	'faculty_id': id
	})

	arr = list(result)

	leaves.approve_leave(arr[0]['name'],'DIRECTOR')

	approved_leaves_list = leaves.approve_leave(arr[0]['name'],'DIRECTOR')
	for i in approved_leaves_list:
		var = contents.find({
			'faculty_id':i[0]
			})

		left = var[0]['leaves_left'] - i[1]

		contents.update_one({'faculty_id':i[0]},{'$set':{
				'leaves_left':left
				}})
	

def director_func(contents):
	print('director access granted')
	print('Enter 1 to view pending leave approval')

	i = (int)(input())

	if i==1:
		view_leave_requests(contents)