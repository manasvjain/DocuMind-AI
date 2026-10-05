from datetime import datetime,timedelta,timezone
import hashlib,hmac,secrets
import jwt
from app.core.config import get_settings
settings=get_settings(); ALGORITHM="HS256"

def hash_password(password:str)->str:
    salt=secrets.token_bytes(16); digest=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1)
    return "scrypt$16384$8$1$"+salt.hex()+"$"+digest.hex()

def verify_password(password,encoded):
    try:
        _,n,r,p,salt_hex,digest_hex=encoded.split("$"); check=hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt_hex),n=int(n),r=int(r),p=int(p)); return hmac.compare_digest(check.hex(),digest_hex)
    except Exception: return False

def create_access_token(subject,role):
    now=datetime.now(timezone.utc); payload={"sub":subject,"role":role,"type":"access","iat":now,"exp":now+timedelta(minutes=settings.jwt_expire_minutes)}; return jwt.encode(payload,settings.jwt_secret,algorithm=ALGORITHM)

def create_refresh_token(subject):
    now=datetime.now(timezone.utc); payload={"sub":subject,"type":"refresh","iat":now,"exp":now+timedelta(days=settings.refresh_token_expire_days)}; return jwt.encode(payload,settings.jwt_secret,algorithm=ALGORITHM)

def decode_token(token:str)->dict: return jwt.decode(token,settings.jwt_secret,algorithms=[ALGORITHM])
