from .models import insert_customer, insert_account, insert_transaction
from db import db

def test_insert_customer():
    sample_customer = {
        "name": {"first": "John", "last": "Doe"},
        "email": "john.doe@example.com",
        "phone": "+1987654321"
    }
    customer_id = insert_customer(sample_customer)
    print(f"Inserted customer ID: {customer_id}")

def test_insert_account():
    sample_account = {
        "customerId": "12345",
        "balance": 1000.00
    }
    account_id = insert_account(sample_account)
    print(f"Inserted account ID: {account_id}")

def test_insert_transaction():
    sample_transaction = {
        "accountId": "12345",
        "amount": 200.00,
        "transaction_type": "deposit"
    }
    transaction_id = insert_transaction(sample_transaction)
    print(f"Inserted transaction ID: {transaction_id}")

# Run all tests
if __name__ == "__main__":
    test_insert_customer()
    test_insert_account()
    test_insert_transaction()
