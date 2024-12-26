from pymongo import MongoClient



from .auth import auth_bp

__all__ = ["auth_bp"]


def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['banking_system']
    return db

db = get_database()
