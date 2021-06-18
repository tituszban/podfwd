import os
from email_exporter import export_inbox

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def handle_request():
    return export_inbox()


@app.route("/fingerprint")
def get_fingerprint():
    return os.environ.get("FINGERPRINT", "")

@app.route("/k")
def get_cloud_run_config():
    return jsonify({
        key: os.environ.get(key, "")
        for key in ("K_SERVICE", "K_REVISION", "K_CONFIGURATION")
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
