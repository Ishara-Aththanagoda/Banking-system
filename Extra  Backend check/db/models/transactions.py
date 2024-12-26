from datetime import datetime
from bson.objectid import ObjectId


def get_transaction_schema(account_id, customer_id, transaction_type, amount, balance_after):
    """
    Returns the transaction schema.
    :param account_id: ObjectId of the associated account.
    :param customer_id: ObjectId of the associated customer.
    :param transaction_type: Type of transaction ("Deposit", "Withdrawal", "Transfer").
    :param amount: Amount of the transaction.
    :param balance_after: Account balance after the transaction.
    :return: Dictionary representing a transaction document.
    """
    return {
        "_id": ObjectId(),
        "accountId": account_id,  # Reference to the Account collection
        "customerId": customer_id,  # Reference to the Customer collection
        "transactionType": transaction_type,
        "amount": amount,
        "date": datetime.now(),
        "balanceAfterTransaction": balance_after
    }


def insert_transaction(db, transaction):
    """
    Inserts a transaction document into the 'transactions' collection.
    :param db: MongoDB database object.
    :param transaction: Dictionary representing the transaction document.
    :return: Inserted ID.
    """
    result = db['transactions'].insert_one(transaction)
    print(f"Transaction inserted with ID: {result.inserted_id}")
    return result.inserted_id


def get_transactions_by_account(db, account_id):
    """
    Retrieves all transactions associated with a specific account.
    :param db: MongoDB database object.
    :param account_id: ObjectId of the account.
    :return: List of transactions.
    """
    transactions = db['transactions'].find({"accountId": account_id})
    return list(transactions)


def get_transactions_by_customer(db, customer_id):
    """
    Retrieves all transactions associated with a specific customer.
    :param db: MongoDB database object.
    :param customer_id: ObjectId of the customer.
    :return: List of transactions.
    """
    transactions = db['transactions'].find({"customerId": customer_id})
    return list(transactions)
