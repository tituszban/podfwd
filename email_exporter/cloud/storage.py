from __future__ import annotations
from email_exporter.config import Config
from google.cloud.storage import Client as StorageClient, Bucket
from typing import Optional
import io


class Storage:
    def __init__(self, bucket: Bucket):
        self._bucket = bucket

    @staticmethod
    def from_client_and_name(client: StorageClient, bucket_name: str) -> Storage:
        bucket = client.get_bucket(bucket_name)
        return Storage(bucket)

    def upload_bytes(self, blob_name: str, content: bytes) -> str:
        blob = self._bucket.blob(blob_name)
        blob.upload_from_file(io.BytesIO(content))
        return blob.public_url

    def upload_xml(self, blob_name: str, content: str) -> str:
        blob = self._bucket.blob(blob_name)
        blob.upload_from_string(content, content_type='text/xml')
        return blob.public_url

    def upload_file_from_path(self, blob_name: str, file_path: str) -> str:
        blob = self._bucket.blob(blob_name)
        with open(file_path, "rb") as f:
            blob.upload_from_file(f)
        return blob.public_url

    def download_xml(self, blob_name: str) -> str:
        blob = self._bucket.blob(blob_name)
        return blob.download_as_string()  # .decode("utf-8")

    def delete_blob(self, blob_name: str) -> None:
        blob = self._bucket.blob(blob_name)
        if blob.exists():
            blob.delete()


class StorageProvider:
    def __init__(self, config: Config, storage_client: StorageClient) -> None:
        self._storage_client = storage_client

    def get_bucket(self, bucket_name: str) -> Optional[Storage]:
        if not bucket_name:
            raise KeyError("Bucket name is missing")
        if not self._storage_client.bucket(bucket_name).exists():
            # TODO: self.create_bucket(bucket_name, true)
            # https://cloud.google.com/storage/docs/access-control/lists#predefined-acl
            return None
        return Storage.from_client_and_name(self._storage_client, bucket_name)

    def create_bucket(self, bucket_name: str, public: bool = False, logging_bucket: Optional[str] = None) -> Storage:
        bucket = self._storage_client.create_bucket(
            bucket_name,
            location="EU",
            predefined_acl="publicRead" if public else "private",
            predefined_default_object_acl="publicRead" if public else "private"
        )
        if logging_bucket:
            bucket.enable_logging(logging_bucket)
        return Storage(bucket)
