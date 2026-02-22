from flask import Blueprint, jsonify, current_app, request

from ..services.email_loader import EmailLoader

emails_bp = Blueprint("emails", __name__)


def get_email_loader() -> EmailLoader:
    """Get EmailLoader from dependencies."""
    return current_app.deps.get(EmailLoader)


@emails_bp.route("/", methods=["GET"])
def list_emails():
    """List all available emails."""
    loader = get_email_loader()
    emails = loader.get_all_emails()

    # Separate by source
    gmail_emails = [e.to_dict() for e in emails if e.source == "gmail"]
    eml_emails = [e.to_dict() for e in emails if e.source == "eml"]

    return jsonify({
        "gmail": gmail_emails,
        "eml": eml_emails
    })


@emails_bp.route("/<email_id>", methods=["GET"])
def get_email(email_id: str):
    """Get a specific email's raw HTML."""
    loader = get_email_loader()
    html = loader.get_raw_html(email_id)

    if html is None:
        return jsonify({"error": "Email not found"}), 404

    return jsonify({"html": html})


@emails_bp.route("/<email_id>/star", methods=["POST"])
def star_email(email_id: str):
    """Mark an email as starred (processed)."""
    loader = get_email_loader()
    data = request.get_json() or {}
    starred = data.get("starred", True)

    loader.mark_starred(email_id, starred)

    return jsonify({"success": True, "starred": starred})


@emails_bp.route("/refresh", methods=["POST"])
def refresh_emails():
    """Force refresh the email list."""
    from ..dependencies import reset_dependencies, get_dependencies
    
    # Reset dependencies to force reload
    reset_dependencies()
    current_app.deps = get_dependencies()

    loader = get_email_loader()
    emails = loader.get_all_emails()

    gmail_emails = [e.to_dict() for e in emails if e.source == "gmail"]
    eml_emails = [e.to_dict() for e in emails if e.source == "eml"]

    return jsonify({
        "gmail": gmail_emails,
        "eml": eml_emails
    })
