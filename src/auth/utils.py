from fastapi.exceptions import HTTPException
from pwdlib import PasswordHash
from datetime import timedelta,datetime,timezone
import jwt
from src.config import Config
import uuid
import logging 
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired, BadSignature


ACCESS_TOKEN_EXPIRY=3600

password_hash = PasswordHash.recommended()
 
def generate_passwd_hash(password:str) -> str:
    passwd_hash = password_hash.hash(password)

    return passwd_hash

def verify_password(password:str,hash:str) -> bool:
    return password_hash.verify(password,hash)


def create_access_token(user_data: dict , expiry:timedelta | None = None, refresh:bool = False) -> dict:
    payload = {}

    payload['user'] = user_data
    payload["exp"] = datetime.now(timezone.utc) + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh


    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_token(token:str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None



serializer = URLSafeTimedSerializer(secret_key=Config.JWT_SECRET)
    
def create_url_safe_token(data:dict) -> str:
    """Serialize a dict into a URLSafe token"""

    token = serializer.dumps(data)

    return token

def decode_url_safe_token(token:str,max_age:int=3600) -> dict:
    """Deserialize a URLSafe token to get data"""
    try:
        data = serializer.loads(token,max_age=max_age)
        return data
    except SignatureExpired:
        raise HTTPException(status_code=400,detail="Token expired")
    except BadSignature:
        raise HTTPException(status_code=400,detail="Invalid token")

    
