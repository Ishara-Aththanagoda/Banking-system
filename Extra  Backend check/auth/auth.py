from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from datetime import datetime


# Initialize auth blueprint and JWTManager
auth_bp = Blueprint('auth', __name__)

# Set a secure secret key for JWT
JWTManager.secret_key = "YourSuperSecureSecretKey"

# MongoDB Connection (use centralized logic)
from db import db


# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    # Validate input
    if not all(key in data for key in ('email', 'password', 'name')):
        return jsonify({"message": "Missing fields"}), 400

    # Prepare data
    hashed_password = generate_password_hash(data['password'], method='bcrypt')
    customer_data = {
        "email": data['email'],
        "password": hashed_password,
        "name": data['name'],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    # Insert customer
    try:
        db.customers.insert_one(customer_data)
        return jsonify({"message": "Account created successfully"}), 201
    except DuplicateKeyError:
        return jsonify({"message": "Email already registered"}), 400
    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

# Login user
@auth_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()

    # Validate input
    if not all(key in data for key in ('email', 'password')):
        return jsonify({"message": "Missing fields"}), 400

    # Fetch user
    customer = db.customers.find_one({"email": data['email']})
    if not customer or not check_password_hash(customer['password'], data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate token
    access_token = create_access_token(
        identity={"id": str(customer['_id']), "email": customer['email']},
        expires_delta=timedelta(hours=1)
    )
    return jsonify({"access_token": access_token}), 200

# Example protected route
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    return jsonify({"message": "Protected route accessed successfully"})

# Error handling for bad requests
@auth_bp.errorhandler(400)
def handle_bad_request(e):
    return jsonify({"message": "Bad request"}), 400

# Error handling for internal server errors
@auth_bp.errorhandler(500)
def handle_internal_error(e):
    return jsonify({"message": "Internal server error"}), 500
