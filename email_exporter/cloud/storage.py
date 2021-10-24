from email_exporter.config import Config
from google.cloud import storage
import io


class StorageProvider:
    def __init__(self, config: Config) -> None:
        json = config.get("SA_FILE")
        if json:
            self.storage_client = storage.Client.from_service_account_json(
                json)
        else:
            self.storage_client = storage.Client()

    def get_bucket(self, bucket_name):
        if not bucket_name:
            raise KeyError("Bucket name is missing")
        if not self.storage_client.bucket(bucket_name).exists():
            # TODO: self.storage_client.create_bucket(bucket_name, predefined_acl=publicRead)
            # https://cloud.google.com/storage/docs/access-control/lists#predefined-acl
            return None
        return Storage.from_client_and_name(self.storage_client, bucket_name)

    def create_bucket(self, bucket_name, public=False):
        bucket = self.storage_client.create_bucket(
            bucket_name,
            location="EU",
            predefined_acl="publicRead" if public else "private",
            predefined_default_object_acl="publicRead" if public else "private"
        )
        return Storage(bucket)


class Storage:
    def __init__(self, bucket):
        self.bucket = bucket

    @staticmethod
    def from_client_and_name(client, bucket_name):
        bucket = client.get_bucket(bucket_name)
        return Storage(bucket)

    def upload_bytes(self, blob_name, content):
        blob = self.bucket.blob(blob_name)
        blob.upload_from_file(io.BytesIO(content))
        return blob.public_url

    def upload_xml(self, blob_name, content):
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content, content_type='text/xml')
        return blob.public_url

    def upload_file_from_path(self, blob_name, file_path):
        blob = self.bucket.blob(blob_name)
        with open(file_path, "rb") as f:
            blob.upload_from_file(f)
        return blob.public_url

    def download_xml(self, blob_name):
        blob = self.bucket.blob(blob_name)
        return blob.download_as_string()  # .decode("utf-8")

    def delete_blob(self, blob_name):
        blob = self.bucket.blob(blob_name)
        blob.delete()
