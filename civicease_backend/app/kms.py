"""Key wrapping. The data key of each document is wrapped by a master key that is kept apart from the data.
LocalKMS: master key from the environment (dev/demo). GcpKMS: Google Cloud KMS, so the master key never leaves KMS."""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class LocalKMS:
    name = "local"

    def __init__(self, master_key: bytes):
        self._aes = AESGCM(master_key)

    def wrap(self, dek: bytes, aad: bytes) -> str:
        nonce = os.urandom(12)
        return base64.b64encode(nonce + self._aes.encrypt(nonce, dek, aad)).decode()

    def unwrap(self, wrapped: str, aad: bytes) -> bytes:
        raw = base64.b64decode(wrapped)
        return self._aes.decrypt(raw[:12], raw[12:], aad)


class GcpKMS:  # pragma: no cover - needs Google credentials
    name = "gcp"

    def __init__(self, key_name: str):
        self.key = key_name  # projects/P/locations/L/keyRings/R/cryptoKeys/K

    def _call(self, op: str, body: dict) -> dict:
        import google.auth
        import google.auth.transport.requests
        import httpx
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(google.auth.transport.requests.Request())
        r = httpx.post(f"https://cloudkms.googleapis.com/v1/{self.key}:{op}", json=body,
                       headers={"Authorization": f"Bearer {creds.token}"}, timeout=15)
        r.raise_for_status()
        return r.json()

    def wrap(self, dek: bytes, aad: bytes) -> str:
        return self._call("encrypt", {"plaintext": base64.b64encode(dek).decode(),
                                      "additionalAuthenticatedData": base64.b64encode(aad).decode()})["ciphertext"]

    def unwrap(self, wrapped: str, aad: bytes) -> bytes:
        return base64.b64decode(self._call("decrypt", {"ciphertext": wrapped,
                                                       "additionalAuthenticatedData": base64.b64encode(aad).decode()})["plaintext"])


def get_kms():
    from app.config import get_settings
    s = get_settings()
    return GcpKMS(s.gcp_kms_key) if s.kms_mode == "gcp" else LocalKMS(s.master_key)
