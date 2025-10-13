from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import logging

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "JWT Marketplace API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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
            user = User.query.filter_by(email=data['email']).first()
            if user is None:
                return jsonify({"error": "User not found"}), 401
            current_user = {
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated_function

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    logger.info(f"Login attempt: {email}")

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        refresh_expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        
        token = jwt.encode({
            'sub': user.email, 'email': user.email, 'role': user.role,
            'name': user.name, 'exp': expiration_time
        }, app.config['JWT_SECRET'], algorithm='HS256')

        refresh_token = jwt.encode({
            'sub': user.email, 'email': user.email, 'exp': refresh_expiration_time
        }, app.config['JWT_SECRET'], algorithm='HS256')

        logger.info(f"Login successful: {email}")
        return jsonify({'access_token': token, 'refresh_token': refresh_token})

    logger.warning(f"Invalid credentials for {email}")
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    data = request.get_json()
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 400

    try:
        data = jwt.decode(refresh_token, app.config['JWT_SECRET'], algorithms=["HS256"])
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({"error": "User not found"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    token = jwt.encode({
        'sub': user.email, 'email': user.email, 'role': user.role,
        'name': user.name, 'exp': expiration_time
    }, app.config['JWT_SECRET'], algorithm='HS256')

    return jsonify({'access_token': token})

@app.route('/items', methods=['GET'])
def get_items():
    items = [
        {"id": 1, "name": "Item 1", "price": 12345},
        {"id": 2, "name": "Item 2", "price": 67890}
    ]
    return jsonify({"items": items})

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    logger.info(f"Profile update attempt for {current_user['email']}")

    if current_user['role'] != 'user':
        logger.warning(f"Permission denied for {current_user['email']}")
        return jsonify({"error": "Permission denied"}), 403

    user_to_update = User.query.filter_by(email=current_user['email']).first()
    if not user_to_update:
        return jsonify({"error": "User not found during update"}), 404

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)
