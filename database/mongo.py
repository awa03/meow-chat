from pymongo import MongoClient

# Connect to the MongoDB server
client = MongoClient('mongodb://localhost:27017/')

# Access the database
db = client['myDatabase']

# Access the collection
collection = db['myCollection']

# Insert a document
collection.insert_one({'name': 'David', 'age': 28})

# Find a document
document = collection.find_one({'name': 'David'})
print(document)

# Update a document
collection.update_one({'name': 'David'}, {'$set': {'age': 29}})

# Delete a document
collection.delete_one({'name': 'David'})

