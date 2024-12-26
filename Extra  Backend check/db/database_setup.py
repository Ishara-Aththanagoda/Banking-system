from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['banking_system']

# Customer Collection
customer = {
    "_id": ObjectId(),
    "name": {"first": "John", "last": "Doe"},
    "email": "johndoe@example.com",
    "phone": "+123456789",
    "address": {"street": "123 Main St", "city": "Example City", "state": "EX", "zip": "12345"},
    "createdAt": datetime.now(),
    "updatedAt": datetime.now()
}
db['customers'].insert_one(customer)

# Account Collection
account = {
    "_id": ObjectId(),
    "customerId": customer["_id"],
    "accountType": "Savings",
    "balance": 5000.00,
    "interestRate": 0.02,
    "createdAt": datetime.now(),
    "updatedAt": datetime.now()
}
db['accounts'].insert_one(account)

# Transaction Collection
transaction = {
    "_id": ObjectId(),
    "accountId": account["_id"],
    "customerId": customer["_id"],
    "transactionType": "Deposit",
    "amount": 1000.00,
    "date": datetime.now(),
    "balanceAfterTransaction": 6000.00
}
db['transactions'].insert_one(transaction)

print("Database and collections created with sample data.")
