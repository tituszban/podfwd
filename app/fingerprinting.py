from . import app
import os
from flask import jsonify


@app.route("/fingerprint")
def get_fingerprint():
    return os.environ.get("FINGERPRINT", "")


@app.route("/k")
def get_cloud_run_config():
    return jsonify({
        key: os.environ.get(key, "")
        for key in ("K_SERVICE", "K_REVISION", "K_CONFIGURATION")
    })
