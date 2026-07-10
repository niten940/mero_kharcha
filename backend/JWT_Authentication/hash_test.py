import bcrypt

def hash_password(password):
    """
    Hashes a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        bytes: The bcrypt-hashed password.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    return hashed

def verify_password(verified_pass,hashed):
    """
    Checks whether a plaintext password matches a bcrypt hash.

    Args:
        verified_pass (str): The plaintext password to check.
        hashed (bytes): The stored bcrypt hash to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(verified_pass.encode('utf-8'),hashed)

password = "mySecret123"
hash_pass = hash_password(password)
print(f"Hashed Password: {hash_pass}")

verified_password = "mySecret123"
if verify_password(verified_password, hash_pass): 
    print("Correct password check: True")
else:
    print("Wrong password check: False")

verified_password = "wrongPassword"
if verify_password(verified_password, hash_pass): 
    print("Correct password check: True")
else:
    print("Wrong password check: False")