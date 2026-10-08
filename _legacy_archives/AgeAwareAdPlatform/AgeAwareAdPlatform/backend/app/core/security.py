import hashlib
import hmac
import json
import base64
import time
from datetime import datetime, timedelta
from typing import Optional
from backend.app.core.config import settings

def hash_password(password: str) -> str:
    """Hashes password securely using SHA-256 with salt fallback."""
    salted = f"{password}{settings.SECRET_KEY}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hash."""
    return hash_password(plain_password) == hashed_password

def _b64url_enc(d: bytes) -> str:
    return base64.urlsafe_b64encode(d).rstrip(b'=').decode('utf-8')

def _b64url_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + '=' * ((4 - len(s) % 4) % 4))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    try:
        from jose import jwt
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    except ImportError:
        # Standard HMAC-SHA256 JWT implementation
        to_encode = data.copy()
        exp_ts = time.time() + (expires_delta.total_seconds() if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        to_encode["exp"] = exp_ts
        header = _b64url_enc(json.dumps({"alg": "HS256", "typ": "JWT"}).encode('utf-8'))
        body = _b64url_enc(json.dumps(to_encode, default=str).encode('utf-8'))
        msg = f"{header}.{body}"
        sig = _b64url_enc(hmac.new(settings.SECRET_KEY.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).digest())
        return f"{msg}.{sig}"

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT token."""
    try:
        from jose import jwt
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ImportError:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            h, b, s = parts
            msg = f"{h}.{b}"
            expected_sig = _b64url_enc(hmac.new(settings.SECRET_KEY.encode('utf-8'), msg.encode('utf-8'), hashlib.sha256).digest())
            if not hmac.compare_digest(s, expected_sig):
                return None
            payload = json.loads(_b64url_dec(b).decode('utf-8'))
            if payload.get("exp") and time.time() > float(payload["exp"]):
                return None
            return payload
        except Exception:
            return None
    except Exception:
        return None
