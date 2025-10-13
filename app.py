from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import logging

# Load environment variables
load_dotenv()

# In-memory user data (demo purpose)
users = {
    "user1@example.com": {
        "password": "pass123",  # In real-world, use hashed passwords
        "name": "User One",
        "email": "user1@example.com",
        "role": "user"  # role-based access: user
    },
    "admin@example.com": {
        "password": "admin123",
        "name": "Admin User",
        "email": "admin@example.com",
        "role": "admin"  # admin role for access control
    }
}

# Setup Flask application and enable CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Swagger UI for OpenAPI Documentation
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # File JSON that contains OpenAPI specs

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "JWT Marketplace API",
        'auth': {
            'bearer': {
                'name': 'Authorization',
                'description': 'Enter your Bearer token',
                'token': 'Bearer <JWT>'
            }
        }
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Decorator to protect routes that require authentication
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({"error": "Missing or invalid Authorization header. Format should be 'Bearer <token>'"}), 401

        try:
            data = jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
            current_user = users.get(data['email'])
            if current_user is None:
                return jsonify({"error": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated_function

# Route for login to obtain JWT
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    logger.info(f"Login attempt: {email}")

    if email in users and users[email]['password'] == password:
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        refresh_expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        token = jwt.encode({
            'sub': email,
            'email': email,
            'role': users[email]['role'],
            'name': users[email]['name'],
            'exp': expiration_time
        }, app.config['JWT_SECRET'], algorithm='HS256')

        refresh_token = jwt.encode({
            'sub': email,
            'email': email,
            'exp': refresh_expiration_time
        }, app.config['JWT_SECRET'], algorithm='HS256')

        logger.info(f"Login successful: {email}")
        return jsonify({'access_token': token, 'refresh_token': refresh_token})

    logger.warning(f"Invalid credentials for {email}")
    return jsonify({"error": "Invalid credentials"}), 401

# Route for refresh token
@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 400

    try:
        data = jwt.decode(refresh_token, app.config['JWT_SECRET'], algorithms=["HS256"])
        current_user = users.get(data['email'])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    token = jwt.encode({
        'sub': data['email'],
        'email': data['email'],
        'role': current_user['role'],
        'name': current_user['name'],
        'exp': expiration_time
    }, app.config['JWT_SECRET'], algorithm='HS256')

    return jsonify({'access_token': token})

# Public endpoint for items
@app.route('/items', methods=['GET'])
def get_items():
    items = [
        {"id": 1, "name": "Item 1", "price": 12345},
        {"id": 2, "name": "Item 2", "price": 67890}
    ]
    return jsonify({"items": items})

# Protected endpoint for profile update
@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    logger.info(f"Profile update attempt for {current_user['email']}")

    if current_user['role'] != 'user':
        logger.warning(f"Permission denied for {current_user['email']}")
        return jsonify({"error": "Permission denied"}), 403

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    if name:
        current_user['name'] = name
    if email:
        current_user['email'] = email

    logger.info(f"Profile updated for {current_user['email']}")
    return jsonify({"message": "Profile updated", "profile": current_user})

if __name__ == '__main__':
    app.run(port=5000)
