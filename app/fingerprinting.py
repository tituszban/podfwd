import os
from flask import jsonify, Blueprint


fingerprinting_blueprint = Blueprint("fingerprinting", __name__)


@fingerprinting_blueprint.route("/fingerprint")
def get_fingerprint():
    return os.environ.get("FINGERPRINT", "")


@fingerprinting_blueprint.route("/k")
def get_cloud_run_config():
    return jsonify({
        key: os.environ.get(key, "")
        for key in ("K_SERVICE", "K_REVISION", "K_CONFIGURATION")
    })
