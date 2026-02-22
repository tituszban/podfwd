"""
Dev API entry point.

Run with: python -m dev_api
Or: flask --app dev_api.app:create_app run --debug --port 5001
"""
from .app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
