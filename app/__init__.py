import os
from flask import Flask
from .fingerprinting import fingerprinting_blueprint
from .exporter import exporter_blueprint
from .feed import feed_blueprint

app = Flask(__name__)

app.register_blueprint(fingerprinting_blueprint)

if os.environ.get("ENABLE_EXPORTER"):
    app.register_blueprint(exporter_blueprint, url_prefix="/exporter")
if os.environ.get("ENABLE_FEED"):
    app.register_blueprint(feed_blueprint)
