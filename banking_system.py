# I'll begin by refactoring the code to implement some of these professional enhancements.
# Here is an outline of the improved code structure:

from typing import List, Optional, Union
from datetime import datetime
import os
import hashlib

# Database simulation as a dictionary for prototype; replace with SQL/NoSQL in production
database = {
    "accounts": [],
    "transactions": [] 
}

# Hashing helper for secure PIN storage
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

# Class Definitions
class Customer:
    def __init__(self, cust_id: str, firstname: str, lastname: str, contact_info: Optional[str] = None):
        self.__cust_id = cust_id
        self.firstname = firstname
        self.lastname = lastname
        self.contact_info = contact_info or "Not provided"
    
    @property
    def customer_id(self):
        return self.__cust_id
    
    def detail(self):
        return f"{self.lastname}, {self.firstname} - Contact: {self.contact_info}"


class Account:
    def __init__(self, customer: Customer, account_no: str, account_type: str, bal: float = 0, pin: str = '0000'):
        self.customer = customer
        self.__account_no = account_no
        self.account_type = account_type
        self.bal = bal
        self.pin = hash_pin(pin)  # Store hashed pin

    @property
    def account_no(self):
        return self.__account_no

    def verify_pin(self, input_pin: str) -> bool:
        return self.pin == hash_pin(input_pin)


class Bank:
    @staticmethod
    def register_customer(cust_id: str, firstname: str, lastname: str, contact_info: Optional[str] = None) -> Customer:
        return Customer(cust_id, firstname, lastname, contact_info)

    @staticmethod
    def create_account(customer: Customer, account_no: str, account_type: str, bal: float = 0, pin: str = '0000') -> Account:
        account = Account(customer, account_no, account_type, bal, pin)
        database["accounts"].append(account)
        return account

    @staticmethod
    def save_transaction(account: Account, amount: float, trxn_type: str):
        today = datetime.today()
        transaction = {
            "date": today.strftime('%Y-%m-%d %H:%M:%S'),
            "account_no": account.account_no,
            "amount": amount,
            "type": trxn_type,
            "balance": account.bal
        }
        database["transactions"].append(transaction)

    @staticmethod
    def account_balance(account: Account) -> float:
        return account.bal

    @staticmethod
    def deposit(account: Account, amount: float) -> str:
        if amount > 0:
            account.bal += amount
            Bank.save_transaction(account, amount, 'credit')
            return "Deposit successful."
        return "Invalid deposit amount."

    @staticmethod
    def withdrawal(account: Account, amount: float) -> str:
        if amount > 0 and account.bal >= amount:
            account.bal -= amount
            Bank.save_transaction(account, -amount, 'debit')
            return "Withdrawal successful."
        return "Insufficient funds or invalid amount."

    @staticmethod
    def transfer(from_account: Account, to_account: Account, amount: float) -> str:
        if from_account.account_no != to_account.account_no and amount > 0 and from_account.bal >= amount:
            from_account.bal -= amount
            to_account.bal += amount
            Bank.save_transaction(from_account, -amount, 'transfer_out')
            Bank.save_transaction(to_account, amount, 'transfer_in')
            return "Transfer successful."
        return "Transfer failed due to insufficient funds or invalid accounts."

    @staticmethod
    def view_transaction_history(account_no: str, limit: int = 5) -> List[dict]:
        return [t for t in database["transactions"] if t["account_no"] == account_no][-limit:]


# Sample Usage with Improvements
customer1 = Bank.register_customer("01", "John", "Doe", "john.doe@example.com")
account1 = Bank.create_account(customer1, "1001", "savings", 1000.0, "1234")

customer2 = Bank.register_customer("02", "Jane", "Smith", "jane.smith@example.com")
account2 = Bank.create_account(customer2, "1002", "checking", 500.0, "5678")

# Perform Transactions
print(Bank.deposit(account1, 200.0))    # Deposit into account1
print(Bank.withdrawal(account2, 50.0))  # Withdraw from account2
print(Bank.transfer(account1, account2, 100.0))  # Transfer from account1 to account2
print(Bank.view_transaction_history("1001", 5))  # View last 5 transactions of account1
