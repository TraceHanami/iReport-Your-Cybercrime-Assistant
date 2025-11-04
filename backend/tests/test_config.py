# test_config.py
# Unified test credentials for all test files

TEST_USERS = {
    "admin": {
        "email": "admin@ireport.com",
        "password": "admin123", 
        "role": "admin"
    },
    "police": {
        "email": "officer@ireport.com", 
        "password": "password123",
        "role": "police"
    },
    "public": {
        "email": "public@ireport.com",
        "password": "password123", 
        "role": "public"
    }
}

BASE_URL = "http://127.0.0.1:5000/api"