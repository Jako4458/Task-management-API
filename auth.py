import json
import bcrypt
import jwt
import secrets
import datetime 

import db
from InvalidInputException import InvalidInputException

jwt_secret_key = ""

# TO avoid timing attacks a random hash is precomputed to compare when users are not found
DUMMY_HASH = bcrypt.hashpw(secrets.token_bytes(32), bcrypt.gensalt()).decode()

def hash_password(password):
    if not isinstance(password, str) or password.strip() == "": raise InvalidInputException("Invalid password: Must be a non-empty string")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def check_password_hash(password, hashed_password):
    if not isinstance(password, str) or password.strip() == "": raise InvalidInputException("Invalid password: Must be a non-empty string")
    if not isinstance(hashed_password, str) or password.strip() == "": raise Exception("Something went wrong")
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def gen_jwt(user):
    payload = {
        'sub': json.dumps({"user_id": user["id"]}),
        'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, jwt_secret_key, algorithm='HS256')
    return token

def verify_jwt(token):
    token = token[len("Bearer "):]
    print("TOKEN: ", token)
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
        return json.loads(payload['sub'])
    except jwt.ExpiredSignatureError:
        return None  
    except jwt.InvalidTokenError:
        return None 

from flask import request, make_response
from functools import wraps

def JWT_required(connection):
    def decorator(func):
        @wraps(func)
        def inner_func(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if auth_header is None:
                return make_response("Unauthorized: Missing token", 401)

            jwt_payload = verify_jwt(auth_header)

            if jwt_payload is None:
                return make_response("Unauthorized: Invalid token", 401)

            user_id = jwt_payload["user_id"]

            if (db.get_user_by_id(user_id, connection) is None):
                return make_response(f"Invalid User: User with id '{user_id}' not found!", 401) 

            return func(*args, user_id=user_id, **kwargs)

        return inner_func

    return decorator

