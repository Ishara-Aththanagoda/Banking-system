import sys
import os
from flask import Flask, jsonify
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import auth_bp  # Authentication blueprint
from transactions.views import transactions_bp  # Transactions blueprint
from db.models import initialize_db  # Function to initialize MongoDB models
from db.encryption import setup_encryption  # Encryption setup
from db.audit import setup_audit_logging  # Audit logging setup
from utils.logging import setup_logging  # Logging utility

from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# App Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Add key')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'uri here')

# Setup Logging
setup_logging('banking_system.log')

# Initialize Database
initialize_db(app.config['MONGO_URI'])

# Setup Encryption
setup_encryption()

# Setup Audit Logging
setup_audit_logging()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(transactions_bp, url_prefix='/transactions')

# Health Check Route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'}), 200

# Error Handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

# Additional Routes (if needed)
@app.route('/info', methods=['GET'])
def app_info():
    return jsonify({
        'app_name': 'Banking System',
        'version': '1.0.0',
        'description': 'A high-security banking system backend.'
    }), 200

# Main Entry Point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
