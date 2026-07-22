from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"

pass_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")
'''
bcrypt is an hashing algorithm that is used specifically for passwords (slow on purpose as it resists against brute force attacks)
unlike MD5/SHA256 which are fast (ideal for file integrity checks or digital signatures) while bcrypt focuses more on password encryption as it 
has salting and GPU Brute Force Defence.

Important note: passwords are always hashed and stored in the db never encrypted as that would introduce security issues (a key would be required to decrypt each pass)
'''

def hash_password(password : str) -> str: # generates a salt, runs the bcrypt algorithm 2^12 times, then merge them
# Algorithm Identifer + Cost Factor (2^12 rounds) + Embedded Random Salt (128 bits) + Final Hash Signtature  
	return pass_context.hash(password)

def verify_password(plain_password: str, hash_password: str) -> bool: # extracts the cost factor and salt from the stored hash and rehashes the entered pass with it
	return pass_context.verify(plain_password, hash_password)

def create_access_token(data: dict, expires_delta : timedelta = timedelta(minutes=30)) -> str:
	to_encode = data.copy() # will return a shallow copy of the dict
	expire = expires_delta + datetime.utcnow() # expire 30 minutes from current time
	to_encode.update({"exp":expire}) # add the expire time into the data that will be added into the payload of the jwt

	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # return the jwt with its data, key and algo