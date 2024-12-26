from datetime import datetime
from bson.objectid import ObjectId

def get_customer_schema():
    return {
        "_id": ObjectId(),
        "name": {"first": "John", "last": "Doe"},
        "email": "johndoe@example.com",
        "phone": "+123456789",
        "address": {"street": "123 Main St", "city": "Example City", "state": "EX", "zip": "12345"},
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
