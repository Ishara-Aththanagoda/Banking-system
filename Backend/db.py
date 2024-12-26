from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import OperationFailure

# MongoDB Connection
def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    return client['banking_system']

db = get_database()

# Audit Logging
def log_audit(action, collection_name, document_id, user_id, details=""):
    """Extended audit logging."""
    db.audit_logs.insert_one({
        "action": action,
        "collection": collection_name,
        "documentId": str(document_id) if document_id else None,
        "userId": user_id,
        "timestamp": datetime.now(),
        "details": details or "No additional details provided"
    })


# Insert Functions
def insert_customer(customer_data, user_id):
    """Insert customer with dynamic data."""
    customer_data["createdAt"] = datetime.now()
    customer_data["updatedAt"] = datetime.now()
    inserted_id = db.customers.insert_one(customer_data).inserted_id
    log_audit("insert", "customers", inserted_id, user_id)
    return inserted_id

def insert_account(account_data, user_id):
    """Insert account with dynamic data."""
    account_data["createdAt"] = datetime.now()
    account_data["updatedAt"] = datetime.now()
    inserted_id = db.accounts.insert_one(account_data).inserted_id
    log_audit("insert", "accounts", inserted_id, user_id) 
    return inserted_id

def insert_transaction(transaction_data, user_id):
    """Insert transaction with dynamic data."""
    transaction_data["date"] = datetime.now()
    inserted_id = db.transactions.insert_one(transaction_data).inserted_id
    log_audit("insert", "transactions", inserted_id, user_id)
    return inserted_id

# Update Functions
def update_account(customer_id, account_updates, user_id):
    """Update account with dynamic data."""
    account_updates["updatedAt"] = datetime.now()
    result = db.accounts.update_one(
        {"customerId": customer_id},
        {"$set": account_updates}
    )
    if result.modified_count > 0:
        log_audit("update", "accounts", customer_id, user_id)
    return result

def delete_account(customer_id, user_id):
    """Delete account by customerId."""
    result = db.accounts.delete_one({"customerId": customer_id})
    if result.deleted_count > 0:
        log_audit("delete", "accounts", customer_id, user_id)
    return result

# Schema Generation
def get_account_schema(customer_id, account_type, balance, user_id):
    """Generate account schema for insertion."""
    return {
        "customerId": customer_id,
        "accountType": account_type,
        "balance": balance,
        "userId": user_id, 
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }

def get_transaction_schema(account_id, customer_id, transaction_type, amount, balance_after):
    """Generate a validated transaction schema."""
    if not isinstance(account_id, str):
        account_id = str(account_id)
    return {
        "accountId": account_id,
        "customerId": customer_id,
        "transactionType": transaction_type,
        "amount": amount,
        "balanceAfterTransaction": balance_after,
        "date": datetime.now()
    }


# Query Functions
def get_account_by_customer_id(customer_id):
    """Fetch an account by customerId."""
    return db.accounts.find_one({"customerId": customer_id})

def get_all_accounts():
    """Fetch all accounts."""
    return list(db.accounts.find())

def get_all_transactions():
    """Fetch all transactions with validation."""
    transactions = list(db.transactions.find())
    for transaction in transactions:
        if "accountId" not in transaction or "date" not in transaction:
            continue  # Skip invalid transactions
        # Convert ObjectId to string if required
        transaction["_id"] = str(transaction["_id"])
    return transactions


# Transaction Process
def process_transaction(account_id, transaction_type, amount, user_id):
    """Process deposit, withdrawal or transfer with error handling and transaction integrity."""
    # Start a session for transaction processing
    session = db.client.start_session()
    try:
        with session.start_transaction():
            account = db.accounts.find_one({"_id": ObjectId(account_id)}, session=session)
            if not account:
                raise ValueError("Account not found")

            if transaction_type == "deposit":
                new_balance = account['balance'] + amount
            elif transaction_type == "withdrawal":
                if account['balance'] < amount:
                    raise ValueError("Insufficient balance")
                new_balance = account['balance'] - amount
            else:
                raise ValueError("Invalid transaction type")

            # Update the account balance
            update_result = db.accounts.update_one(
                {"_id": ObjectId(account_id)},
                {"$set": {"balance": new_balance, "updatedAt": datetime.now()}},
                session=session
            )
            if update_result.modified_count == 0:
                raise OperationFailure("Failed to update account balance")

            # Insert the transaction record
            transaction_data = get_transaction_schema(account_id, account['customerId'], transaction_type, amount, new_balance)
            insert_transaction(transaction_data, user_id)

            # Log audit for transaction
            log_audit("transaction", "transactions", account_id, user_id, f"{transaction_type} of {amount} successful")

        session.commit_transaction()
        return {"status": "success", "new_balance": new_balance}

    except Exception as e:
        session.abort_transaction()
        log_audit("transaction_error", "transactions", account_id, user_id, str(e))
        return {"status": "failure", "message": str(e)}
    finally:
        session.end_session()

# Index Creation
def create_indexes():
    """Create necessary indexes for the collections."""
    # Ensure unique index on `customerId` in `accounts`
    existing_indexes = db.accounts.index_information()
    if "customerId_1" in existing_indexes:
        if not existing_indexes["customerId_1"].get("unique", False):
            db.accounts.drop_index("customerId_1")
            print("Dropped non-unique index on `customerId` in `accounts`.")

    db.accounts.create_index("customerId", unique=True)
    print("Created unique index on `customerId` in `accounts`.")

    # Index on `accountId` in `transactions`
    if "accountId_1" not in db.transactions.index_information():
        db.transactions.create_index("accountId")
        print("Created index on `accountId` in `transactions`.")

# Encryption Functions (Placeholder)
def encrypt_data(data, key):
    """Encrypt data (placeholder)."""
    # Add actual encryption logic here
    return data  # Placeholder for encrypted data

def decrypt_data(data, key):
    """Decrypt data (placeholder)."""
    # Add actual decryption logic here
    return data  # Placeholder for decrypted data

# Example Usage
if __name__ == "__main__":
    # Ensure indexes are created
    create_indexes()

    # Example: Process a deposit transaction
    result = process_transaction("account_id_here", "deposit", 500.00, user_id="admin_user")
    print(result)

    # Example: Process a withdrawal transaction
    result = process_transaction("account_id_here", "withdrawal", 200.00, user_id="admin_user")
    print(result)
