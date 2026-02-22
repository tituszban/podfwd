from flask import Blueprint, jsonify, current_app

from ..services.email_loader import EmailLoader
from ..services.parser_service import ParserService

parse_bp = Blueprint("parse", __name__)


def get_email_loader() -> EmailLoader:
    """Get EmailLoader from dependencies."""
    return current_app.deps.get(EmailLoader)


def get_parser_service() -> ParserService:
    """Get ParserService from dependencies."""
    return current_app.deps.get(ParserService)


@parse_bp.route("/<email_id>", methods=["GET"])
def parse_email(email_id: str):
    """Parse an email and return detailed results."""
    loader = get_email_loader()
    parser_service = get_parser_service()

    inbox_item = loader.get_email(email_id)
    if inbox_item is None:
        return jsonify({"error": "Email not found"}), 404

    result = parser_service.parse_email(inbox_item)

    return jsonify(result.to_dict())


@parse_bp.route("/<email_id>/refresh", methods=["POST"])
def refresh_parse(email_id: str):
    """Force re-parse an email (useful after code changes)."""
    from ..dependencies import reset_dependencies, get_dependencies
    
    # Reset dependencies to pick up code changes
    reset_dependencies()
    current_app.deps = get_dependencies()

    loader = get_email_loader()
    parser_service = get_parser_service()

    inbox_item = loader.get_email(email_id)
    if inbox_item is None:
        return jsonify({"error": "Email not found"}), 404

    result = parser_service.parse_email(inbox_item)

    return jsonify(result.to_dict())
