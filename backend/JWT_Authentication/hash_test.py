import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The bcrypt-hashed password as a UTF-8 string.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    """
    Check whether a plaintext password matches a bcrypt hash.

    Args:
        plaintext (str): The plaintext password to verify.
        hashed (str): The stored bcrypt hash to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))