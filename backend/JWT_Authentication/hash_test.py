import bcrypt


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Return string, not bytes

<<<<<<< HEAD
def verify_password(verified_pass, hashed):
    # hashed is now a string from DB
    return bcrypt.checkpw(verified_pass.encode('utf-8'), hashed.encode('utf-8'))
=======
    Args:
        password (str): The plaintext password to hash.

    Returns:
        bytes: The bcrypt-hashed password.
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed


def verify_password(verified_pass, hashed):
    """
    Checks whether a plaintext password matches a bcrypt hash.

    Args:
        verified_pass (str): The plaintext password to check.
        hashed (bytes): The stored bcrypt hash to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(verified_pass.encode("utf-8"), hashed)

>>>>>>> edb0151c31f03a79e09fcc4010f69994c6c2a6b3

password = "mySecret123"
hash_pass = hash_password(password)
# print(f"Hashed Password: {hash_pass}")

test_password = "Paisa#Deu"
# if verify_password(verified_password, hash_pass):
#     print("Correct password check: True")
# else:
#     print("Wrong password check: False")

# verified_password = "wrongPassword"
# if verify_password(verified_password, hash_pass):
#     print("Correct password check: True")
# else:
#     print("Wrong password check: False")
