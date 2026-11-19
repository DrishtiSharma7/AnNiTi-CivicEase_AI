"""Private object storage for encrypted blobs. Local disk for dev; GCS keeps the API stateless so it can autoscale."""
import shutil
from pathlib import Path

from app.config import get_settings


class LocalStorage:
    def __init__(self, root: str):
        self.root = Path(root).resolve()

    def _p(self, key: str) -> Path:
        p = (self.root / key).resolve()
        if self.root not in p.parents:
            raise ValueError("bad storage key")
        return p

    def put(self, key: str, data: bytes) -> None:
        p = self._p(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def get(self, key: str) -> bytes:
        return self._p(key).read_bytes()

    def delete(self, key: str) -> None:
        self._p(key).unlink(missing_ok=True)

    def delete_prefix(self, prefix: str) -> None:
        shutil.rmtree(self._p(prefix.rstrip("/")), ignore_errors=True)


class GcsStorage:  # pragma: no cover - needs Google credentials
    def __init__(self, bucket: str):
        from google.cloud import storage
        self.bucket = storage.Client().bucket(bucket)

    def put(self, key: str, data: bytes) -> None:
        self.bucket.blob(key).upload_from_string(data, content_type="application/octet-stream")

    def get(self, key: str) -> bytes:
        return self.bucket.blob(key).download_as_bytes()

    def delete(self, key: str) -> None:
        b = self.bucket.blob(key)
        if b.exists():
            b.delete()

    def delete_prefix(self, prefix: str) -> None:
        for b in self.bucket.list_blobs(prefix=prefix):
            b.delete()


_instance = None


def get_storage():
    global _instance
    if _instance is None:
        s = get_settings()
        _instance = GcsStorage(s.gcs_bucket) if s.storage_backend == "gcs" else LocalStorage(s.storage_dir)
    return _instance
