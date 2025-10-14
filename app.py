from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from flask_cors import CORS
import logging

# Muat environment variables dari file .env
load_dotenv()

# Inisialisasi aplikasi Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Konfigurasi dari environment variables
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfigurasi Template untuk Flasgger agar sesuai dengan swagger.json
# Ini adalah kunci untuk memunculkan tombol "Authorize"
template = {
    "swagger": "2.0",
    "info": {
        "title": "JWT Marketplace API",
        "description": "API for a simple marketplace with JWT authentication.",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your JWT in the format: Bearer <token>"
        }
    },
}

# Inisialisasi Flasgger dengan template
swagger = Swagger(app, template=template)

# Inisialisasi database dan logging
db = SQLAlchemy(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model Database untuk User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100))
    role = db.Column(db.String(50), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Decorator untuk proteksi endpoint dengan JWT
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Authentication token is missing or invalid"}), 401

        try:
            data = jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
            user = User.query.filter_by(email=data['email']).first()
            if user is None:
                return jsonify({"error": "User not found"}), 404
            current_user = {"email": user.email, "name": user.name, "role": user.role}
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)

    return decorated_function

# Endpoint Pemeriksaan Kesehatan
@app.route('/')
def index():
    """Endpoint to check if the server is running."""
    return jsonify({"status": "ok", "message": "API server is running!"})

# Endpoint untuk Otentikasi
@app.route('/auth/login', methods=['POST'])
def login():
    """
    Login and get JWT
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        description: User credentials
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: user1@example.com
            password:
              type: string
              example: pass123
    responses:
      200:
        description: Successfully logged in and received access token
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    logger.info(f"Login attempt: {email}")

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
        refresh_expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
        
        token = jwt.encode({'sub': user.email, 'email': user.email, 'role': user.role, 'name': user.name, 'exp': expiration_time}, app.config['JWT_SECRET'], algorithm='HS256')
        refresh_token = jwt.encode({'sub': user.email, 'email': user.email, 'exp': refresh_expiration_time}, app.config['JWT_SECRET'], algorithm='HS256')

        logger.info(f"Login successful: {email}")
        return jsonify({'access_token': token, 'refresh_token': refresh_token})

    logger.warning(f"Invalid credentials for {email}")
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh access token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        description: Provide the refresh token to get a new access token
        required: true
        schema:
          type: object
          properties:
            refresh_token:
              type: string
    responses:
      200:
        description: Access token refreshed successfully
      401:
        description: Invalid or expired refresh token
    """
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"error": "Refresh token not found"}), 400

    try:
        data = jwt.decode(refresh_token, app.config['JWT_SECRET'], algorithms=["HS256"])
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Refresh token is invalid"}), 401

    expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
    token = jwt.encode({'sub': user.email, 'email': user.email, 'role': user.role, 'name': user.name, 'exp': expiration_time}, app.config['JWT_SECRET'], algorithm='HS256')

    return jsonify({'access_token': token})

# Endpoint untuk Item
@app.route('/items', methods=['GET'])
def get_items():
    """
    Get list of marketplace items
    ---
    tags:
      - Items
    responses:
      200:
        description: List of items
    """
    items = [
        {"id": 1, "name": "Item 1", "price": 12345},
        {"id": 2, "name": "Item 2", "price": 67890}
    ]
    return jsonify({"items": items})

# Endpoint untuk Profil Pengguna
@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Update user profile
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        description: Updated user information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
    responses:
      200:
        description: Profile updated
      401:
        description: Invalid token
      403:
        description: Permission denied
      404:
        description: User not found
    """
    logger.info(f"Profile update attempt for {current_user['email']}")

    if current_user['role'] != 'user':
        logger.warning(f"Permission denied for {current_user['email']}")
        return jsonify({"error": "Permission denied"}), 403

    user_to_update = User.query.filter_by(email=current_user['email']).first()
    if not user_to_update:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if data.get('name'):
        user_to_update.name = data.get('name')
    if data.get('email'):
        user_to_update.email = data.get('email')
    
    db.session.commit()

    logger.info(f"Profile updated for {user_to_update.email}")
    return jsonify({
        "message": "Profile updated", 
        "profile": {"name": user_to_update.name, "email": user_to_update.email}
    })

# Menjalankan aplikasi
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=int(os.getenv('PORT', 5000)))

