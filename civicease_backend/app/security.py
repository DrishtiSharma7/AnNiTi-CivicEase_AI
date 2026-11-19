"""Cryptographic primitives (pure, no web framework imports).

- Argon2id password hashing
- JWT access tokens
- SHA-256 file fingerprints
- Salted HMAC-SHA256 digests for sensitive IDs (never store raw)
- AES-256-GCM envelope encryption: unique data key per document, wrapped by a master key (KMS stand-in)
- HMAC-signed, expiring tokens: signed file URLs and the human approval token
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional

import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def b64u_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def form_hash(form: dict) -> str:
    """Hash of the exact form shown to the citizen; the approval token is bound to it."""
    return sha256_hex(canonical_json(form).encode())


# ---- passwords -------------------------------------------------------------
def hash_password(password: str) -> str:
    from argon2 import PasswordHasher
    return PasswordHasher().hash(password)


def verify_password(hashed: str, password: str) -> bool:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError, InvalidHashError
    try:
        return PasswordHasher().verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


# ---- JWT -------------------------------------------------------------------
def create_access_token(sub: str, secret: str, minutes: int) -> str:
    now = int(time.time())
    return jwt.encode({"sub": sub, "iat": now, "exp": now + minutes * 60}, secret, algorithm="HS256")


def decode_access_token(token: str, secret: str) -> Optional[str]:
    try:
        return jwt.decode(token, secret, algorithms=["HS256"], options={"require": ["exp", "sub"]})["sub"]
    except jwt.PyJWTError:
        return None


# ---- sensitive IDs ---------------------------------------------------------
def new_salt() -> str:
    return secrets.token_hex(16)


def _normalize_id(value: str) -> str:
    return "".join(ch for ch in value if ch.isalnum()).upper()


def id_digest(value: str, salt: str, pepper: str) -> str:
    """Salted HMAC-SHA256 digest used for matching; the raw value is never stored."""
    key = hashlib.sha256((pepper + salt).encode()).digest()
    return hmac.new(key, _normalize_id(value).encode(), hashlib.sha256).hexdigest()


def mask_id(value: str) -> str:
    v = _normalize_id(value)
    return ("*" * max(len(v) - 4, 0)) + v[-4:]


# ---- envelope encryption ---------------------------------------------------
def encrypt_document(plaintext: bytes, kms, aad: bytes) -> tuple:
    """Returns (blob, wrapped_key). Unique AES-256 data key per document; the key is wrapped by the KMS
    and stored apart from the encrypted file. aad binds the ciphertext to user and document."""
    dek = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    blob = nonce + AESGCM(dek).encrypt(nonce, plaintext, aad)
    return blob, kms.wrap(dek, aad)


def decrypt_document(blob: bytes, wrapped: str, kms, aad: bytes) -> bytes:
    dek = kms.unwrap(wrapped, aad)
    return AESGCM(dek).decrypt(blob[:12], blob[12:], aad)


# ---- signed, expiring tokens ----------------------------------------------
def derive_key(pepper: str, purpose: str) -> bytes:
    return hmac.new(pepper.encode(), purpose.encode(), hashlib.sha256).digest()


def sign_payload(payload: dict, key: bytes, ttl_seconds: int) -> str:
    body = dict(payload, exp=int(time.time()) + ttl_seconds)
    raw = canonical_json(body).encode()
    sig = hmac.new(key, raw, hashlib.sha256).digest()
    return f"{b64u(raw)}.{b64u(sig)}"


def verify_payload(token: str, key: bytes) -> Optional[dict]:
    try:
        raw_b64, sig_b64 = token.split(".", 1)
        raw, sig = b64u_decode(raw_b64), b64u_decode(sig_b64)
        if not hmac.compare_digest(hmac.new(key, raw, hashlib.sha256).digest(), sig):
            return None
        body = json.loads(raw)
        if int(body.get("exp", 0)) < time.time():
            return None
        return body
    except Exception:
        return None


# ---- service-to-service request signing (API -> browser worker) -------------
def sign_request(secret: str, timestamp: int, body: bytes) -> str:
    return hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()


def verify_request(secret: str, timestamp: int, body: bytes, signature: str, max_skew: int = 60) -> bool:
    if abs(time.time() - timestamp) > max_skew:
        return False
    return hmac.compare_digest(sign_request(secret, timestamp, body), signature)
