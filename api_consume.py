import requests
import json
import jwt as pyjwt


SECRET_KEY = 'ahmedsaad'


def register_user(first_name, last_name, email, password, phone_number):
    url = 'http://localhost:5000/register'  # Replace with your API endpoint

    data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'phone_number': phone_number
    }

    token = get_token('user', 'password')
    print(token)
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, headers=headers, json=data)
    return response.json()




def get_token(username, password):
    url = 'http://localhost:5000/login'  
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['token']
    else:
        return None

# Register a user
response = register_user('Ahmed', 'Saad', 'ahmedsaad@example.com', 'password123', '1234567890')
print(response)


