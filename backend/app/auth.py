import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("SECRET_KEY", "polychat-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Hachage PBKDF2-SHA256 — module Python intégré, aucune dépendance externe
_ITERATIONS = 260_000

security = HTTPBearer()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS)
    return f"pbkdf2:sha256:{_ITERATIONS}:{salt}:{h.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        _, algo, iterations, salt, expected = hashed.split(":")
        h = hashlib.pbkdf2_hmac(algo, plain.encode(), salt.encode(), int(iterations))
        return secrets.compare_digest(h.hex(), expected)
    except Exception:
        return False


def create_token(username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré, veuillez vous reconnecter")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    return decode_token(credentials.credentials)


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return user


def verify_ws_token(token: str = Query(...)) -> dict:
    """Dépendance pour valider le token JWT passé en query param sur WebSocket."""
    return decode_token(token)
