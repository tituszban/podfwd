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
    firestore_client.collection = MagicMock(return_value=db_client)

    collection_name = "collection_name"
    config = Mock()
    config.get = MagicMock(return_value=collection_name)

    owner = "item_owner"
    item = Mock()
    item.owner = owner
    item.sender = "sender"

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
    db_document_client.get = MagicMock(return_value=db_document)
    db_client = Mock()
    db_client.document = MagicMock(return_value=db_document_client)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    item = Mock()
    item.owner = "owner"
    item.sender = "sender"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == VOICE_DEFAULT


def _mock_firestore_client_with_voice_data(data):
    def _get_document(document):
        db_document = Mock()
        db_document.exists = document in data
        db_document.to_dict = MagicMock(return_value=data[document] if document in data else {})
        db_document_client = Mock()
        db_document_client.get = MagicMock(return_value=db_document)
        return db_document_client

    db_client = Mock()
    db_client.document = MagicMock(side_effect=_get_document)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)
    return firestore_client


def test_get_voice_falls_back_to_global_document_domain():
    voice = "voice_name"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                voice: [
                    {"always": True}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = "sender"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_finds_global_domain_in_owner_document():
    voice = "voice_name"
    owner = "owner_value"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            }
        },
        owner: {
            GLOBAL_DOMAIN: {
                voice: [
                    {"always": True}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = owner
    item.sender = "sender"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_sender_domain_always():
    voice = "voice_name"
    sender_domain = "sender_domain"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                voice: [
                    {"always": True}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"sender@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_sender_domain_ignore_always_false():
    voice = "voice_name"
    sender_domain = "sender_domain"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                "false_voice": [
                    {"always": False}
                ],
                voice: [
                    {"always": True}
                ]
            }
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
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                voice: [
                    {"sender": sender_name}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"{sender_name}@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_rule_sender_contains():
    voice = "voice_name"
    sender_domain = "sender_domain"
    sender_name = "sender_name"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                voice: [
                    {"sender_contains": sender_name[3:8]}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"{sender_name}@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_rule_subject_contains():
    voice = "voice_name"
    sender_domain = "sender_domain"
    subject = "item_subject_value"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                voice: [
                    {"subject_contains": subject[3:8]}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"sender@{sender_domain}"
    item.title = subject

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_rule_object_is_and():
    voice = "voice_name"
    sender_domain = "sender_domain"
    subject = "item_subject_value"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                "other_voice": [
                    {"subject_contains": subject[3:8], "always": False}
                ],
                voice: [
                    {"subject_contains": subject[3:8], "always": True}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"sender@{sender_domain}"
    item.title = subject

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_rule_collection_is_or():
    voice = "voice_name"
    sender_domain = "sender_domain"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                voice: [
                    {"always": False},
                    {"always": True}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"sender@{sender_domain}"

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
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                "other_voice": [
                    {"sender": sender_name}
                ]
            }
        },
        owner: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                voice: [
                    {"sender": sender_name}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = owner
    item.sender = f"{sender_name}@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice


def test_get_voice_global_document_default_rule_is_false():
    voice = "voice_name"
    sender_domain = "sender_domain"
    data = {
        GLOBAL_DOCUMENT: {
            GLOBAL_DOMAIN: {
                "other_voice": [
                    {"always": True}
                ]
            },
            sender_domain: {
                "other_voice": [
                    {"bad_rule_name": True}
                ],
                voice: [
                    {"always": True}
                ]
            }
        }
    }
    firestore_client = _mock_firestore_client_with_voice_data(data)

    item = Mock()
    item.owner = "owner"
    item.sender = f"sender@{sender_domain}"

    sut = VoiceProvider(Mock(), Mock(), firestore_client)

    result = sut.get_voice(item)

    assert result == voice
