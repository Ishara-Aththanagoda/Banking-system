import bcrypt
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timezone 
from bson import ObjectId
import openai
from flask_cors import cross_origin
import requests
import sympy as sp 
from transformers import pipeline
from dotenv import load_dotenv
import os

load_dotenv()

from db import (
    get_database,
    insert_customer,
    insert_account,
    insert_transaction,
    log_audit, 
    create_indexes,
    get_account_schema,
    get_transaction_schema,
)


class Config:
    #JWT_SECRET_KEY = 'key'
    #MONGO_URI = 'uri'  


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


#CORS(app, origins="http://localhost:3000", supports_credentials=True)


jwt = JWTManager(app)


db = get_database()


create_indexes()

#openai.api_key = "my-key"

chatbot = pipeline('text-generation', model='microsoft/DialoGPT-medium')


@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        required_fields = ['email', 'password', 'name']
        
        # Check if required fields are provided
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify(message=f"Missing fields: {', '.join(missing_fields)}"), 400
        
        # Check if email already exists in the database
        existing_customer = db.customers.find_one({"email": data['email']})
        if existing_customer:
            return jsonify(message="Email already registered"), 400
        
        # Hash the password before storing using bcrypt
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create a unique customer ID
        user_id = str(ObjectId())  
        
        # Create the customer document
        customer_data = {
            "_id": user_id,  
            "name": data['name'],
            "email": data['email'],
            "password": hashed_password,
            "createdAt": datetime.now(timezone.utc),  
            "updatedAt": datetime.now(timezone.utc)
        }
        
        # Insert customer into the database
        db.customers.insert_one(customer_data)
        
        # Return a successful response
        return jsonify(message="Account created successfully", customer_id=user_id), 201
    
    except Exception as e:
        app.logger.error(f"Error during registration: {e}")
        return jsonify(message="An error occurred during registration"), 500


@app.route('/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'message': 'CORS preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

   
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify(message="Missing email or password"), 400

    customer = db.customers.find_one({"email": data['email']})
    if customer and bcrypt.checkpw(data['password'].encode('utf-8'), customer['password'].encode('utf-8')):
        token = create_access_token(identity={"email": customer['email'], "name": customer['name']})
        return jsonify(access_token=token), 200
    return jsonify(message="Invalid credentials"), 401

# Account Management
@app.route('/accounts/create', methods=['POST'])
def create_account():
    try:
        print("Request received at /accounts/create")
        data = request.json
        print(f"Request data: {data}")

        customer_id = data.get('customerId')
        account_type = data.get('accountType', 'Savings')
        balance = data.get('balance', 0.0)
        user_id = data.get('userId')  

        if not customer_id or not user_id:  
            print("Customer ID or User ID is missing")
            return jsonify({"error": "Customer ID and User ID are required"}), 400

        print(f"Creating account schema with: customerId={customer_id}, accountType={account_type}, balance={balance}, userId={user_id}")
        account_data = get_account_schema(customer_id, account_type, balance, user_id)  # Pass userId to the schema function

        print(f"Generated account schema: {account_data}")
        account_id = insert_account(account_data, user_id)  # Pass userId to insert function

        print(f"Account successfully created with ID: {account_id}")
        return jsonify({"message": "Account created successfully", "accountId": str(account_id)}), 201
    except Exception as e:
        print(f"Error in /accounts/create: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/accounts/update', methods=['POST'])
def update_account():
    data = request.get_json()
    account_id = data.get('customerId')
    account_type = data.get('accountType')
    balance = data.get('balance')

    if not account_id:
        return jsonify(message="Missing customer ID"), 400

    # Find the account in the database
    account = db.accounts.find_one({"customerId": account_id})
    if not account:
        return jsonify(message="Account not found"), 404

    # Update account fields
    db.accounts.update_one({"customerId": account_id}, {"$set": {
        "accountType": account_type,
        "balance": balance
    }})

    return jsonify(message="Account updated successfully"), 200

@app.route('/accounts/delete', methods=['POST'])
def delete_account():
    data = request.get_json()
    account_id = data.get('customerId')

    if not account_id:
        return jsonify(message="Missing customer ID"), 400

    # Find and delete the account
    account = db.accounts.find_one({"customerId": account_id})
    if not account:
        return jsonify(message="Account not found"), 404

    db.accounts.delete_one({"customerId": account_id})

    return jsonify(message="Account deleted successfully"), 200

# Route for handling transactions (Transfer)
@app.route('/api/transactions/transfer', methods=['POST'])
def transfer_funds():
    data = request.json
    try:
        from_account = data.get('fromAccount')
        to_account = data.get('toAccount')
        amount = float(data.get('amount'))
        description = data.get('description', '')

        # Simulate the transaction logic
        if not from_account or not to_account or amount <= 0:
            return jsonify({"message": "Invalid transaction details"}), 400

        # Success response (replace with actual DB insert/update logic)
        return jsonify({"message": "Transaction completed successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/transactions/history', methods=['GET'])
@jwt_required()
def get_transaction_history():
    try:
        # Get current user identity from JWT
        current_user = get_jwt_identity()
        app.logger.info(f"JWT Identity: {current_user}")

        if not current_user:
            app.logger.error("JWT Identity is missing or invalid.")
            return jsonify({'message': 'Invalid token or identity not found'}), 401

        # Extract account_id from the JWT payload
        user_account = current_user.get('account_id') if isinstance(current_user, dict) else current_user
        if not user_account:
            app.logger.error(f"Account ID missing in JWT payload: {current_user}")
            return jsonify({'message': 'Account ID not found in token', 'jwt_payload': current_user}), 422

        # Fetch transaction history for the user's account
        transactions = list(db.transactions.find({
            '$or': [
                {'fromAccount': user_account},
                {'toAccount': user_account}
            ]
        }, {'_id': 0}))  # Exclude '_id' if not needed

        if not transactions:
            return jsonify({'message': 'No transactions found'}), 404

        return jsonify({'history': transactions}), 200

    except Exception as e:
        app.logger.error(f"Error fetching transaction history: {e}")
        return jsonify({'message': 'Error fetching transaction history'}), 500


# AI Chat Endpoint
@app.route('/api/ai-assistant/chat', methods=['POST'])
def ai_chat():
    data = request.json
    user_query = data.get('query', '')

    if not user_query:
        return jsonify({'error': 'Query cannot be empty.'}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI Assistant."},
                {"role": "user", "content": user_query}
            ],
            max_tokens=150
        )
        assistant_reply = response['choices'][0]['message']['content'].strip()
        return jsonify({'reply': assistant_reply}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Translation Endpoint
@app.route('/api/ai-assistant/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Text cannot be empty.'}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator. Translate the following text into French."},
                {"role": "user", "content": text}
            ],
            max_tokens=100
        )
        translation = response['choices'][0]['message']['content'].strip()
        return jsonify({'translation': translation}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Math Solver Endpoint
@app.route('/api/ai-assistant/solve-math', methods=['POST'])
def solve_math():
    data = request.json
    problem = data.get('problem', '')

    if not problem:
        return jsonify({'error': 'Problem cannot be empty.'}), 400

    try:
        solution = sp.sympify(problem)
        result = sp.simplify(solution)
        return jsonify({'solution': str(result)}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid math problem: ' + str(e)}), 400

# Weather Information Endpoint
@app.route('/api/ai-assistant/weather', methods=['POST'])
def weather():
    data = request.json
    location = data.get('location', '')

    if not location:
        return jsonify({'error': 'Location cannot be empty.'}), 400

    try:
        # Example using OpenWeatherMap API
        #api_key = "key"
        #url = f"uri"
        response = requests.get(url)
        weather_data = response.json()

        if response.status_code == 200:
            # Format the weather information as per the specified JSON structure
            weather_info = {
                "city": weather_data['name'],
                "description": weather_data['weather'][0]['description'].capitalize(),
                "temperature": weather_data['main']['temp']
            }
            return jsonify(weather_info), 200
        else:
            return jsonify({'error': weather_data.get('message', 'Unable to fetch weather data.')}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/api/galaxy/chat', methods=['POST'])
def chat():
    # Get user input from the request body (JSON)
    user_input = request.json.get('user_input', '')
    
    if not user_input:
        return jsonify({'error': 'No user input provided'}), 400
    
    # Generate the chatbot response
    response = chatbot(user_input, max_length=1000, num_return_sequences=1)
    
    # Extract the generated text from the response
    generated_response = response[0]['generated_text']
    
    return jsonify({'response': generated_response})

    
# User Information Route
@app.route('/auth/me', methods=['GET'])
def get_user_info():
    # Your logic to get the user's data or profile
    return jsonify({"message": "User information"}), 200

@app.route('/auth/me', methods=['OPTIONS'])
def options_me():
    return '', 200


# Error Handlers
@app.errorhandler(400)
def handle_bad_request(e):
    return jsonify(message="Bad request", error=str(e)), 400

@app.errorhandler(401)
def handle_unauthorized(e):
    return jsonify(message="Unauthorized access", error=str(e)), 401

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify(message="Resource not found", error=str(e)), 404

@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify(message="Internal server error", error=str(e)), 500

# Main Execution
if __name__ == '__main__':
    app.run(debug=True)
