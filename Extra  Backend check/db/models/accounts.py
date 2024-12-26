from datetime import datetime
from bson.objectid import ObjectId


def get_account_schema(customer_id):
    """
    Returns the account schema with a reference to the customer ID.
    :param customer_id: ObjectId of the associated customer.
    :return: Dictionary representing an account document.
    """
    return {
        "_id": ObjectId(),
        "customerId": customer_id,  # Reference to the Customer collection
        "accountType": "Savings",  # Options: "Savings", "Checking", "Loan", etc.
        "balance": 5000.00,  # Default starting balance
        "interestRate": 0.02,  # Default interest rate for savings accounts (2%)
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }


def insert_account(db, account):
    """
    Inserts an account document into the 'accounts' collection.
    :param db: MongoDB database object.
    :param account: Dictionary representing the account document.
    :return: Inserted ID.
    """
    result = db['accounts'].insert_one(account)
    print(f"Account inserted with ID: {result.inserted_id}")
    return result.inserted_id


def get_accounts_by_customer(db, customer_id):
    """
    Retrieves all accounts associated with a specific customer.
    :param db: MongoDB database object.
    :param customer_id: ObjectId of the customer.
    :return: List of accounts.
    """
    accounts = db['accounts'].find({"customerId": customer_id})
    return list(accounts)
