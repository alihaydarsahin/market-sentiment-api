import requests
import json
from base64 import b64encode

def get_auth_header(username, password):
    """Generate Basic Auth header"""
    credentials = b64encode(f"{username}:{password}".encode()).decode()
    return {'Authorization': f'Basic {credentials}'}

def test_api():
    """Test API endpoints with authentication"""
    base_url = 'http://localhost:5000/api'
    
    # Test login
    auth_header = get_auth_header('admin', 'admin123')
    response = requests.post(f'{base_url}/login', headers=auth_header)
    print("\nLogin Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        token = response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test protected endpoints
        endpoints = [
            ('GET', '/health'),
            ('POST', '/predict', {'reddit_sentiment': 0.5}),
            ('GET', '/data/latest'),
            ('GET', '/model/info')
        ]
        
        for method, endpoint, *data in endpoints:
            print(f"\nTesting {endpoint}:")
            if method == 'GET':
                response = requests.get(f'{base_url}{endpoint}', headers=headers)
            else:
                response = requests.post(f'{base_url}{endpoint}', 
                                      headers=headers, 
                                      json=data[0])
            print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    test_api() 