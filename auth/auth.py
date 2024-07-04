import hashlib

USERS_FILE = 'data/users.txt'

ADMIN_USERNAME = 'TVA'
ADMIN_PASSWORD = 'TVA'

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Check if the username and password match a stored user or admin."""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return 'admin'
    if authenticate_user(username, password):
        return 'user'
    return None

def authenticate_user(username, password):
    """Check if the username and password match a stored user."""
    try:
        with open(USERS_FILE, 'r') as file:
            for line in file:
                stored_user, stored_password = line.strip().split(':')
                if stored_user == username and stored_password == hash_password(password):
                    return True
    except FileNotFoundError:
        pass
    return False

def add_user(username, password):
    """Add a new user with a hashed password."""
    if user_exists(username):
        return False
    with open(USERS_FILE, 'a') as file:
        file.write(f"{username}:{hash_password(password)}\n")
    return True

def user_exists(username):
    """Check if the username already exists."""
    try:
        with open(USERS_FILE, 'r') as file:
            for line in file:
                stored_user, _ = line.strip().split(':')
                if stored_user == username:
                    return True
    except FileNotFoundError:
        pass
    return False
