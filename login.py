import bcrypt
import setup_database
import otp_management

def check_password(plain_text_password, salt, stored_hash):
    password_bytes = plain_text_password.encode('utf-8')
    
    # Ensure salt and stored_hash are bytes
    if isinstance(salt, str):
        salt = salt.encode('utf-8')
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
        
    # Calculate hash with the provided salt
    calculated_hash = bcrypt.hashpw(password_bytes, salt)
    
    # Compare calculated hash with the stored hash
    return calculated_hash == stored_hash

def collect_user_details_for_login():
    user_email = input("Enter your email address: ")
    user_password = input("Enter your password: ")
    conn = setup_database.get_db_connection()
    if not conn:
        return
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (user_email,))
    result = cursor.fetchone()
    if result:
        salt = result[3]
        hashed_password = result[2]
 #       print(f"DEBUG: Retrieved salt: {salt!r}")
 #       print(f"DEBUG: Retrieved hash: {hashed_password!r}")
        if check_password(user_password, salt, hashed_password):
            print("Login successful.")
            return [user_email, salt, hashed_password]
        else:
            print("Login failed.")
            return False
    else:
        print("Login failed.")
        return False

def main():
#CHECK DETAILS
    correct_details = False
    while correct_details == False:
        correct_details = collect_user_details_for_login()
    print("DEBUG: correct_details --> ", correct_details)
#CHECK OTP
    otp = otp_management.generate_otp(correct_details[0])
    user_otp = input("Enter the OTP sent to your email: ")
    otp_verified = False
    if otp == user_otp:
        otp_verified = True
    while otp_verified == False:
        otp = otp_management.generate_otp(correct_details[0])
        user_otp = input("Enter the OTP sent to your email: ")
        if user_otp == otp:
            print("OTP verified successfully.")
            otp_verified = True
        else:
            print("OTP verification failed.")
            print("Please try again.")
    print("Access to the full system granted...")
    return [otp_verified, correct_details[0]]



if __name__ == "__main__":
    main()