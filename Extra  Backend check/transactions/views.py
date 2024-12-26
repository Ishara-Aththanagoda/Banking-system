from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from db.models import insert_transaction
from db import db
from db.audit import log_audit




# Initialize the transactions blueprint
transactions_bp = Blueprint('transactions', __name__)

# Deposit funds
@transactions_bp.route('/deposit', methods=['POST'])
@jwt_required()
def deposit():
    try:
        data = request.get_json()

        # Validate input data
        if not data or 'account_id' not in data or 'amount' not in data:
            return jsonify(message="Invalid input: account_id and amount are required"), 400

        account_id = data['account_id']
        amount = data['amount']

        # Ensure amount is valid
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify(message="Invalid amount: must be a positive number"), 400

        # Find the account
        account = db.accounts.find_one({"_id": ObjectId(account_id)})
        if not account:
            return jsonify(message="Account not found"), 404

        # Update the account balance
        new_balance = account['balance'] + amount
        db.accounts.update_one({"_id": ObjectId(account_id)}, {"$set": {"balance": new_balance}})

        # Record the transaction
        insert_transaction({
            'accountId': account_id,
            'amount': amount,
            'transaction_type': 'deposit',
            'user_email': get_jwt_identity()['email']
        })

        # Log the audit
        log_audit("deposit", "accounts", account_id, get_jwt_identity()['email'])

        return jsonify(message="Deposit successful", balance=new_balance), 200

    except Exception as e:
        return jsonify(message="An error occurred", error=str(e)), 500

# Withdraw funds
@transactions_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    try:
        data = request.get_json()

        # Validate input data
        if not data or 'account_id' not in data or 'amount' not in data:
            return jsonify(message="Invalid input: account_id and amount are required"), 400

        account_id = data['account_id']
        amount = data['amount']

        # Ensure amount is valid
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify(message="Invalid amount: must be a positive number"), 400

        # Find the account
        account = db.accounts.find_one({"_id": ObjectId(account_id)})
        if not account:
            return jsonify(message="Account not found"), 404

        # Ensure sufficient funds
        if account['balance'] < amount:
            return jsonify(message="Insufficient funds"), 400

        # Update the account balance
        new_balance = account['balance'] - amount
        db.accounts.update_one({"_id": ObjectId(account_id)}, {"$set": {"balance": new_balance}})

        # Record the transaction
        insert_transaction({
            'accountId': account_id,
            'amount': amount,
            'transaction_type': 'withdraw',
            'user_email': get_jwt_identity()['email']
        })

        # Log the audit
        log_audit("withdraw", "accounts", account_id, get_jwt_identity()['email'])

        return jsonify(message="Withdrawal successful", balance=new_balance), 200

    except Exception as e:
        return jsonify(message="An error occurred", error=str(e)), 500