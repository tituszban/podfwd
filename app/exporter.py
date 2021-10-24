from email_exporter.individual import export_inbox
from . import app


@app.route("/", methods=["GET"])
@app.route("/exporter/run", methods=["GET"])
def run_exporter_get():
    return "Email exporter must be invoked with POST"


@app.route("/", methods=["POST"])
@app.route("/exporter/run", methods=["POST"])
def run_exporter():
    return export_inbox()
