from os import getenv

from itsdangerous import URLSafeSerializer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeSerializer(getenv("SECRET_KEY", "dev-secret"))

ADMIN_USERNAME = getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = getenv("ADMIN_PASSWORD_HASH", "")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain[:72], hashed)


def create_session(data: dict) -> str:
    return serializer.dumps(data)


def read_session(token: str) -> dict:
    return serializer.loads(token)
