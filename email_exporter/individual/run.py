from ..email_exporter import EmailExporter
from ..inbox import Inbox
from ..shared import Dependencies
from firebase_admin import firestore


def clone_collection(collection_from_name, collection_to_name):
    deps = Dependencies()
    firestore_client = deps.get(firestore.Client)

    collection_from = firestore_client.collection(collection_from_name)
    collection_to = firestore_client.collection(collection_to_name)

    for document in collection_from.get():
        collection_to.document(document.id).set(
            document.to_dict()
        )

    return "Success: Clone"


def export_inbox():
    deps = Dependencies()

    email_exporter = deps.get(EmailExporter)
    inbox = deps.get(Inbox)

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success: Export inbox"
