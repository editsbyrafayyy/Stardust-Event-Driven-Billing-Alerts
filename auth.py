from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from config import settings
from fastapi.security import OAuth2PasswordBearer
from db import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from models import User

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # tells /docs that /login is the endpoint that issues tokens
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

# when the user logs in the first time, this is called
def create_access_token(data: dict, expires_delta : timedelta = timedelta(minutes=30)) -> str:
	to_encode = data.copy() # will return a shallow copy of the dict
	expire = expires_delta + datetime.now(timezone.utc) # expire 30 minutes from current time
	to_encode.update({"exp":expire}) # add the expire time into the data that will be added into the payload of the jwt

	return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # return the jwt with its data, key and algo

# Now, this function extracts the token from HTTP Auth header
# this only works once the user has logged in once and now is sending subsequent requests
def get_user_from_token(token: str, db: Session) -> User: # before the function runs
	# the oauth2_scheme value is calculated as it is a dependency same for get_db

	credentials_exception = HTTPException(
		status_code= status.HTTP_401_UNAUTHORIZED,
		detail= "Incorrect Credentials"
		)

	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # decode the jwt and store it
		username: str = payload.get("sub") # extract the subject which is a unqiue identifier 
		
		if username is None: # if it doesn't exist
			raise credentials_exception # raise the exception
		
	except JWTError: # if any error occured during the try statement
		raise credentials_exception # raise this

	user = db.query(User).filter(User.username == username).first() # check if the user even exists (extra measure of sec)
	if user is None:
		raise credentials_exception
	return user

# and now the token is already recieved it just needs to be verified (as WebSockets don't expect a Auth Header instead a query string) so now it gets the token from the query header
# this way we are able to reuse the same logic for both HTTP (expects Auth Header) and WebSockets (expect query string) without having to change the behaviour
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
	return get_user_from_token(token, db)