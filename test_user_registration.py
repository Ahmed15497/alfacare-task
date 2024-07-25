import pytest
from main import app, db, User  # Replace with your actual app and db imports
import json
from api_consume import get_token


# Ensure database is in memory for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ahmed:ahmed@localhost:3306/store_test'
app.config['TESTING'] = True
USERNAME, PASSWORD = 'user', 'password'

# Create a test client
client = app.test_client()

# Create database tables before each test
@pytest.fixture(scope='function')
def db_session():
    with app.test_request_context():
        db.create_all()
        yield db  # provide access to session
        db.session.remove()
        db.drop_all()



def test_register_success(db_session):
    data = {
        "first_name": "Ahmed",
        "last_name": "Saad",
        "email": "AhmedSaad@example.com",
        "password": "password123",
        "phone_number": "+966512345678"
    }
    # Generate a valid token (replace with your token generation logic)
    token = get_token(USERNAME, PASSWORD)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/register', json=data, headers=headers)
    assert response.status_code == 201
    assert response.json['message'] == 'User registration successful'

def test_register_missing_fields(db_session):
    data = {
        "first_name": "Ahmed",
        "last_name": "Saad",
        "email": "AhmedSaad@example.com",
        "password": "password123"
    }

    # Generate a valid token (replace with your token generation logic)
    token = get_token(USERNAME, PASSWORD)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/register', json=data, headers=headers)

    assert response.status_code == 400
    assert response.json['error'] == 'Missing required fields'

def test_register_invalid_email(db_session):
    data = {
        "first_name": "Ahmed",
        "last_name": "Saad",
        "email": "invalid_email",
        "password": "password123",
        "phone_number": "+966512345678"
    }

    # Generate a valid token (replace with your token generation logic)
    token = get_token(USERNAME, PASSWORD)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/register', json=data, headers=headers)

    assert response.status_code == 400
    assert 'Invalid email format' in response.json['error']

def test_register_existing_email(db_session):
    # Create a user first
    user = User(first_name="Ahmed", last_name="Saad", email="AhmedSaad@example.com", password="password", phone_number="+966512345678")
    db.session.add(user)
    db.session.commit()

    data = {
        "first_name": "Ahmed",
        "last_name": "Saad",
        "email": "AhmedSaad@example.com",
        "password": "password123",
        "phone_number": "+966512345678"
    }

    # Generate a valid token (replace with your token generation logic)
    token = get_token(USERNAME, PASSWORD)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/register', json=data, headers=headers)
     
    assert response.status_code == 409
    assert response.json['error'] == 'Email already exists'

def test_register_long_fields(db_session):
    """Tests registration with excessively long fields"""
    data = {
        "first_name": "x" * 101,
        "last_name": "x" * 101,
        "email": "valid_email@example.com",
        "password": "password123",
        "phone_number": "+966512345678"
    }
    # Generate a valid token (replace with your token generation logic)
    token = get_token(USERNAME, PASSWORD)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/register', json=data, headers=headers)    
    assert response.status_code == 500  


def test_register_special_characters(db_session):
    """Tests registration with special characters"""
    data = {
        "first_name": "Ahmed@",
        "last_name": "Saad!",
        "email": "valid_email@example.com",
        "password": "password123",
        "phone_number": "+966512345678"
    }

    # Generate a valid token (replace with your token generation logic)
    token = get_token(USERNAME, PASSWORD)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/register', json=data, headers=headers)

    assert response.status_code == 400 

def test_register_empty_fields(db_session):
    """Tests registration with empty required fields"""
    data = {
        "first_name": "",
        "last_name": "Saad",
        "email": "valid_email@example.com",
        "password": "password123",
        "phone_number": "+966512345678"
    }
    # Generate a valid token (replace with your token generation logic)
    token = get_token(USERNAME, PASSWORD)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/register', json=data, headers=headers)

    assert response.status_code == 400 