from flask import Blueprint
from email_exporter.individual import export_inbox

exporter_blueprint = Blueprint("exporter", __name__)


@exporter_blueprint.route("/run", methods=["GET"])
def run_exporter_get():
    return "Email exporter must be invoked with POST"


@exporter_blueprint.route("/run", methods=["POST"])
def run_exporter():
    return export_inbox()
