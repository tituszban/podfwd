from mock import Mock
from email_exporter.cloud.storage import Storage


def test_from_client_and_name():
    bucket = Mock()
    client = Mock()
    client.get_bucket.return_value = bucket

    bucket_name = "bucket_name"

    storage = Storage.from_client_and_name(client, bucket_name)

    client.get_bucket.assert_called_with(bucket_name)

    assert storage._bucket == bucket
