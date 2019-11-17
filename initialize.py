from pymongo import MongoClient
import leaves
client = MongoClient('mongodb://localhost:27017')
db = client['project_nosql']
contents = db.contents
print(contents)

# leaves.initialize()

def get_cursor():
	return contents