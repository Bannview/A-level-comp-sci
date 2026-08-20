import bcrypt

def hash_password(plain_text_password):
    password_bytes = plain_text_password.encode('utf-8') #bytes

    salt = bcrypt.gensalt() #salt=key
    print(f"Salt (store this too!): {salt}")
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return [salt, hashed_password]

def check_password(plain_text_password, salt, hashed_password):
    password_bytes = plain_text_password.encode('utf-8')
    candidate_hash = bcrypt.hashpw(password_bytes, salt)
    return candidate_hash == hashed_password
    

