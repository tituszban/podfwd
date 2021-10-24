import os
from flask import Flask

app = Flask(__name__)

from .fingerprinting import *       # noqa: F403, F401, E402

if os.environ.get("ENABLE_EXPORTER"):
    from .exporter import *       # noqa: F403, F401
