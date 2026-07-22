import bcrypt


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # Return string, not bytes

def verify_password(verified_pass, hashed):
    # hashed is now a string from DB
    return bcrypt.checkpw(verified_pass.encode('utf-8'), hashed.encode('utf-8'))

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
