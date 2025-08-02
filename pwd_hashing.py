import bcrypt
import secrets

# TO avoid timing attacks a random hash is precomputed to compare when users are not found
DUMMY_HASH = bcrypt.hashpw(secrets.token_bytes(32), bcrypt.gensalt())

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def check_password_hash(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)