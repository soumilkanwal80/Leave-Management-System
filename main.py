from pymongo import MongoClient
import pprint
import admin
import faculty
import leaves
import deanfa
import hod
import director
import initialize

default_leaves = 15




# while True:
# 	s = input('Enter login id:')
# 	#print(s)
# 	if s=='admin':
# 		admin.admin_func(contents)
# 		break
# 	elif s=='faculty':
# 		faculty.faculty_func(contents)
# 		break	
# 	elif s=='deanfa':
# 		deanfa.deanfa_func(contents)
# 		break
# 	elif s=='hod':
# 		hod.hod_func(contents)
# 		break
# 	elif s=='director':
# 		director.director_func(contents)
# 		break		
# 	else:
# 		print('Login id is not present in database.')
