from mock import Mock, MagicMock
from email_exporter.voice_provider import CreatorVoiceProvider
from email_exporter.voice_provider.creator_voice_provider import VOICE_KEY
from email_exporter.voice_provider.voice_provider import VOICE_DEFAULT


def test_get_voice_loads_documents():
    db_document_client = Mock()
    db_document_client.get = MagicMock()
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    owner = "item_owner"
    item = Mock()
    item.owner = owner
    item.sender = "sender"

    sut = CreatorVoiceProvider(config, Mock(), firestore_client)

    sut.get_voice(item)

    firestore_client.collection.assert_called_once_with(collection_name)
    db_client.document.assert_called_once_with(owner)
    db_document_client.get.assert_called_once()


def test_get_voice_document_doesnt_exists_return_default():
    document = Mock()
    document.exists = False
    db_document_client = Mock()
    db_document_client.get.return_value = document
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    item = Mock()
    item.owner = "owner"

    sut = CreatorVoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == VOICE_DEFAULT


def test_get_voice_uses_voice_in_document():
    voice = "voice_name"
    document_data = {
        VOICE_KEY: voice
    }

    document = Mock()
    document.exists = True
    document.to_dict.return_value = document_data
    db_document_client = Mock()
    db_document_client.get.return_value = document
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    item = Mock()
    item.owner = "owner"

    sut = CreatorVoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_no_voice_in_document_uses_default():
    document_data = {}

    document = Mock()
    document.exists = True
    document.to_dict.return_value = document_data
    db_document_client = Mock()
    db_document_client.get.return_value = document
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    item = Mock()
    item.owner = "owner"

    sut = CreatorVoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == VOICE_DEFAULT
