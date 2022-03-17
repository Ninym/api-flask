import pymongo
import os

# Initalization Start

MongoURI = os.environ.get('MONGO_URL', None) 
database = pymongo.MongoClient(MongoURI)   # Create Connection to MongoDB

# Initalization End

def UrlParser(operation):
    if operation == add
