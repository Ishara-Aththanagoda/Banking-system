from pymongo import MongoClient
from datetime import datetime

# Step 1: Connect to MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    print("MongoDB connected successfully!")
except Exception as e:
    print("Error connecting to MongoDB:", e)

# Step 2: Access/Create the database
db = client['banking_system']  # Create or access 'banking_system' database
print(f"Database '{db.name}' connected.")

# Step 3: Optional - Test a collection
test_collection = db['test']
test_collection.insert_one({"message": "Connection Successful", "timestamp": datetime.now()})
print("Test document inserted into 'test' collection.")
