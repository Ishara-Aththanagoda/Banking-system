from datetime import datetime
from . import db  # Import the database connection

# Insert a customer
def insert_customer(customer_data):
    customer_data['createdAt'] = datetime.now()
    customer_data['updatedAt'] = datetime.now()
    result = db.customers.insert_one(customer_data)
    return result.inserted_id

# Insert an account
def insert_account(account_data):
    account_data['createdAt'] = datetime.now()
    account_data['updatedAt'] = datetime.now()
    result = db.accounts.insert_one(account_data)
    return result.inserted_id

# Insert a transaction
def insert_transaction(transaction_data):
    transaction_data['date'] = datetime.now()
    result = db.transactions.insert_one(transaction_data)
    return result.inserted_id

def create_indexes():
    db.accounts.create_index("customerId")
    db.transactions.create_index("accountId")


from . import db

def insert_transaction(transaction_data):
    transactions_collection = db['transactions']
    return transactions_collection.insert_one(transaction_data)

def insert_account(account_data):
    accounts_collection = db['accounts']
    return accounts_collection.insert_one(account_data)

def initialize_db():
    from . import db  # Import db only when needed
    # Perform initialization logic
    pass

def initialize_db():
    from . import db  # Import only when needed
    # Perform initialization logic (e.g., creating indexes)
    print("Database initialized successfully.")


