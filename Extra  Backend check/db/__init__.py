from pymongo import MongoClient



def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['banking_system']
    return db

db = get_database()
