import os
from flask import Flask

app = Flask(__name__)

if os.environ.get("ENABLE_FINGERPRINTING"):
    from .fingerprinting import *       # noqa: F403, F401
if os.environ.get("ENABLE_EXPORTER"):
    from .exporter import *       # noqa: F403, F401
