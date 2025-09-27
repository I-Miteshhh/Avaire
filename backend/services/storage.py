from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

try:  # pragma: no cover - optional dependency
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except Exception:  # pragma: no cover - boto3 is optional
    boto3 = None
    BotoCoreError = ClientError = Exception


class StorageBackend(str, Enum):
    LOCAL = "local"
    S3 = "s3"


@dataclass
class StorageConfig:
    backend: StorageBackend
    local_root: Path
    public_url: Optional[str]
    bucket_name: Optional[str]
    region: Optional[str]

    @classmethod
    def from_env(cls) -> "StorageConfig":
        backend = StorageBackend(os.getenv("STORAGE_BACKEND", "local").lower())
        local_root = Path(os.getenv("STORAGE_LOCAL_ROOT", "storage"))
        public_url = os.getenv("STORAGE_PUBLIC_URL")
        bucket = os.getenv("S3_BUCKET_NAME")
        region = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION"))
        return cls(backend=backend, local_root=local_root, public_url=public_url, bucket_name=bucket, region=region)


@dataclass
class StoredObject:
    relative_path: str
    local_path: Path
    url: str


class StorageClient:
    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        self.config.local_root.mkdir(parents=True, exist_ok=True)
        self._s3 = None

        if self.config.backend == StorageBackend.S3:
            if boto3 is None:
                raise RuntimeError("boto3 is required for S3 storage backend. Install boto3 and try again.")
            if not self.config.bucket_name:
                raise RuntimeError("S3_BUCKET_NAME must be set when using S3 storage backend")

            self._s3 = boto3.client("s3", region_name=self.config.region)

    def write_bytes(self, relative_path: str, data: bytes, content_type: Optional[str] = None) -> StoredObject:
        key = self._normalise(relative_path)
        local_path = self.config.local_root / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)

        if self._s3 is not None:
            self._upload_file(local_path, key, content_type)

        return StoredObject(relative_path=key, local_path=local_path, url=self.get_public_url(key))

    async def save_upload(self, upload: UploadFile, relative_path: str) -> StoredObject:
        data = await upload.read()
        return self.write_bytes(relative_path, data, content_type=upload.content_type)

    def sync(self, relative_path: str, content_type: Optional[str] = None) -> StoredObject:
        key = self._normalise(relative_path)
        local_path = self.config.local_root / key
        if not local_path.exists():
            raise FileNotFoundError(f"Local file {local_path} does not exist")
        if self._s3 is not None:
            self._upload_file(local_path, key, content_type)
        return StoredObject(relative_path=key, local_path=local_path, url=self.get_public_url(key))

    def resolve_local_path(self, resource: str) -> Path:
        key = self._normalise(resource)
        return self.config.local_root / key

    def get_public_url(self, resource: str) -> str:
        key = self._normalise(resource)
        if self._s3 is not None and self.config.bucket_name:
            if self.config.public_url:
                base = self.config.public_url.rstrip("/")
                return f"{base}/{key}"
            suffix = f".s3.{self.config.region}.amazonaws.com" if self.config.region else ".s3.amazonaws.com"
            return f"https://{self.config.bucket_name}{suffix}/{key}"
        return f"/storage/{key}"

    def ensure_directory(self, relative_dir: str) -> Path:
        key = self._normalise(relative_dir)
        path = self.config.local_root / key
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _normalise(self, resource: str) -> str:
        normalised = resource.replace("\\", "/").lstrip("/")
        if normalised.startswith("storage/"):
            normalised = normalised.split("storage/", 1)[1]
        return normalised

    def _upload_file(self, local_path: Path, key: str, content_type: Optional[str] = None) -> None:
        if self._s3 is None:
            return
        extra_args = {"ACL": "public-read"}
        if content_type:
            extra_args["ContentType"] = content_type
        try:
            self._s3.upload_file(str(local_path), self.config.bucket_name, key, ExtraArgs=extra_args)
        except (BotoCoreError, ClientError) as exc:  # pragma: no cover - network call
            raise RuntimeError(f"Failed to upload {key} to S3: {exc}") from exc


_storage_client: Optional[StorageClient] = None


def get_storage_client() -> StorageClient:
    global _storage_client
    if _storage_client is None:
        config = StorageConfig.from_env()
        _storage_client = StorageClient(config)
    return _storage_client
