from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
import re
import jwt as pyjwt
import functools
import time

app = Flask(__name__)

# Configure database connection details (replace with your actual settings)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://ahmed:ahmed@localhost:3306/store"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Recommended for performance
app.config['SECRET_KEY'] = 'ahmedsaad'  # Replace with a strong secret key


db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


    def __init__(self, first_name, last_name, email, phone_number, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = self.__hash_password(password)


    def __hash_password(self, password):
        """
        Hashes a string using the SHA-256 algorithm.

        Args:
            password (str): The string to be hashed.

        Returns:
            str: The hashed password in hexadecimal format.
        """

        # Encode the password as bytes (UTF-8 is a common encoding)
        password_bytes = password.encode('utf-8')

        # Create a SHA-256 hash object
        hash_object = hashlib.sha256(password_bytes)
        hash_object = hash_object.hexdigest()


        return hash_object
    
    def __validate_password(self, hashed_password, password):
        """
        Validates a password against a stored hashed password.

        Args:
            hashed_password (str): The stored hashed password (SHA-256 hexdigest).
            password (str): The password to be validated.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """

        # Hash the provided password using the same hashing method
        password_hash = self.__hash_password(password)

        # Compare the hashed password with the stored hash
        return password_hash == hashed_password   

    def check_password(self, password):
        return self.__validate_password(self.password_hash, password)
    

def validate_email(email):
  """
  Validates an email address using a regular expression.

  Args:
      email (str): The email address to be validated.

  Returns:
      bool: True if the email is valid, False otherwise.
  """

  # Email validation regex (source: https://www.regular-expressions.info/email.html)
  email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"

  # Check if the email matches the regex
  return bool(re.match(email_regex, email))

def validate_saudi_phone_number(phone_number):
  """
  Validates a Saudi Arabian phone number using a regular expression.

  Args:
      phone_number (str): The phone number to be validated.

  Returns:
      bool: True if the phone number is valid, False otherwise.
  """

  # Saudi Arabian phone number regex (mobile and landline)
  saudi_phone_regex = r"^((?:\+966)?(5|0)(5|0|3|6|4|9|1|8|7)\d{7})$"

  # Check if the phone number matches the regex
  return bool(re.match(saudi_phone_regex, phone_number))

def validate_name(name):
  """
  Validates a name to ensure it contains only alphabetic characters.

  Args:
      name (str): The name to be validated.

  Returns:
      bool: True if the name is valid, False otherwise.
  """

  name_regex = r'^[a-zA-Z]+$'
  return bool(re.match(name_regex, name))


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': time.time() + 300  # Expires in 5 minutes
    }
    token = pyjwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token



def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = pyjwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(data, *args, **kwargs)

    return decorated


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Replace this with your actual user authentication logic
    if username == 'user' and password == 'password':
        token = generate_token(123)  # Replace 123 with actual user ID
        #token = token.decode('utf-8')  # Assuming UTF-8 encoding
        #print(token)
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/create_tables')
@token_required
def create_tables(token_data):
    with app.app_context():
        db.create_all()
    return jsonify({'message': 'Tables created successfully'}), 201


@app.route('/register', methods=['POST'])
@token_required
def register(token_data):
    data = request.get_json()

    if not data or not all(field in data for field in ['first_name', 'last_name', 'email', 'password', 'phone_number']):
        return jsonify({'error': 'Missing required fields'}), 400  # Bad request

    # Validate email
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400  # Bad request

    # Validate phone number
    if not validate_saudi_phone_number(data['phone_number']):
        return jsonify({'error': 'Invalid phone format'}), 400  # Bad request

    # Validate name
    if (not validate_name(data['first_name'])) or (not validate_name(data['last_name'])):
        return jsonify({'error': 'Invalid names'}), 400  # Bad request

    # Check for existing user
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409  # Conflict

    # Hash password
    user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone_number=data['phone_number'],  
        password=data['password']
    )

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registration successful'}), 201  # Created
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'error': 'Server error occurred'}), 500  # Internal server error



if __name__ == '__main__':
    app.run(debug=True, port=5000)

