import sys; sys.path.insert(0,'backend')
from app.core.security import create_access_token,decode_token,hash_password,verify_password
def test_password_hash_roundtrip():
    encoded=hash_password('correct horse battery staple'); assert encoded.startswith('scrypt$'); assert verify_password('correct horse battery staple',encoded); assert not verify_password('wrong',encoded)
def test_jwt_roundtrip():
    payload=decode_token(create_access_token('user-1','VIEWER')); assert payload['sub']=='user-1' and payload['role']=='VIEWER' and payload['type']=='access'
