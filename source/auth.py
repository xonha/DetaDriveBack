import os
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    secret_key = os.environ["DETA_PROJECT_KEY"]
    algorithm = "HS256"

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, payload: dict):
        return jwt.encode(
            {"exp": datetime.utcnow() + timedelta(hours=12), **payload},
            self.secret_key,
            algorithm=self.algorithm,
        )

    def decode_token(self, token):
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_middleware(
        self,
        request: Request,
        auth: HTTPAuthorizationCredentials = Security(security),
    ):
        request.state.user_credentials = self.decode_token(auth.credentials)
