from mock import Mock, MagicMock
from email_exporter.voice_provider import VoiceProvider
from email_exporter.voice_provider.voice_provider import GLOBAL_DOCUMENT, GLOBAL_DOMAIN, VOICE_DEFAULT


def test_get_voice_loads_documents():
    documents = {}

    def _get_document(document):
        db_document_client = Mock()
        db_document_client.get = MagicMock()
        documents[document] = db_document_client
        return db_document_client

    db_client = Mock()
    db_client.document = MagicMock(side_effect=_get_document)
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    owner = "item_owner"
    item = Mock()
    item.owner = owner
    item.sender = "sender@domain"

    sut = VoiceProvider(config, Mock(), firestore_client)

    sut.get_voice(item)

    assert owner in documents
    assert GLOBAL_DOCUMENT in documents

    firestore_client.collection.assert_called_once_with(collection_name)
    documents[owner].get.assert_called_once()
    documents[GLOBAL_DOCUMENT].get.assert_called_once()


def test_get_voice_no_data_returns_default():
    db_document = Mock()
    db_document.exists = False
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    item = Mock()
    item.owner = "owner"
    item.sender = "sender@domain"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == VOICE_DEFAULT


def _mock_firestore_client_with_voice_data(data):
    def _get_document(document):
        db_document = Mock()
        db_document.exists = document in data
        db_document.to_dict.return_value = data[document] if document in data else {}
        db_document_client = Mock()
        db_document_client.get.return_value = db_document
        return db_document_client

    db_client = Mock()
    db_client.document = MagicMock(side_effect=_get_document)
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client
    return firestore_client


def test_get_voice_falls_back_to_global_document_domain():
    voice = "voice_name"
    data = {
        GLOBAL_DOCUMENT: {
            "*@*": voice
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = "sender@domain"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_finds_global_domain_in_owner_document():
    voice = "voice_name"
    owner = "owner_value"
    data = {
        GLOBAL_DOCUMENT: {
            "*@*": "other_voice"
        },
        owner: {
            "*@*": voice
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = owner
    item.sender = "sender@domain"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_sender_domain_always():
    voice = "voice_name"
    sender_domain = "sender_domain"
    data = {
        GLOBAL_DOCUMENT: {
            "*@*": "other_voice",
            f"*@{sender_domain}": voice
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"sender@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_rule_sender():
    voice = "voice_name"
    sender_domain = "sender_domain"
    sender_name = "sender_name"
    data = {
        GLOBAL_DOCUMENT: {
            "*@*": "other_voice",
            f"{sender_name}@{sender_domain}": voice
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"{sender_name}@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_owner_document_rule_sender():
    voice = "voice_name"
    owner = "owner_value"
    sender_domain = "sender_domain"
    sender_name = "sender_name"
    data = {
        GLOBAL_DOCUMENT: {
            "*@*": "other_voice",
            f"{sender_name}@{sender_domain}": "other_voice"
        },
        owner: {
            "*@*": "other_voice",
            f"{sender_name}@{sender_domain}": voice
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = owner
    item.sender = f"{sender_name}@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice
