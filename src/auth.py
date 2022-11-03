import os
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = os.getenv("DETA_PROJECT_KEY")

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self):
        payload = {
            "exp": datetime.utcnow() + timedelta(hours=12),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_token(self, token):
        try:
            jwt.decode(token, self.secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")
