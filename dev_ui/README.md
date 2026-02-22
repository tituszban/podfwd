# PODFWD Dev UI

A development UI for debugging and testing the PODFWD email-to-podcast parser.

## Features

- View emails from Gmail IMAP and `.eml` files in the `sources/` folder
- Side-by-side comparison of original HTML and generated SSML/description
- Debug information for each parsed section
- On-demand audio generation with caching
- Live reload support for rapid iteration

## Setup

### Backend (Flask API)

1. Install the main project requirements:
```bash
pip install -r requirements.txt
```

2. Install the dev API requirements:
```bash
pip install -r dev_api/requirements.txt
```

3. Set up environment variables (same as main app, plus):
```bash
# Gmail IMAP credentials (for loading emails from inbox)
export AP_EMAIL_SERVER=imap.gmail.com
export AP_EMAIL_LOGIN=your-email@gmail.com
export AP_EMAIL_PASSWORD=your-app-password

# Google Cloud credentials for TTS
export AP_SA_FILE=/path/to/service-account.json
export AP_PROJECT_ID=your-project-id

# Optional
export AP_HUMAN_READABLE_LOGS=true
```

4. Run the dev API:
```bash
# From the autopod directory
python -m dev_api
```

The API will be available at `http://localhost:5001`

### Frontend (React + Vite)

1. Install dependencies:
```bash
cd dev_ui
npm install
```

2. Run the development server:
```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

## Usage

1. Start both the backend and frontend
2. Emails will be loaded automatically from:
   - Gmail IMAP (unflagged emails)
   - `.eml` files in the `sources/` folder (recursive scan)
3. Click on an email to view its parsed content
4. Use the tabs to switch between SSML, Description, and Audio views
5. Click "Generate" to create audio for SSML chunks (cached by content hash)
6. Click "Refresh Parse" to re-parse after code changes

## API Endpoints

### Emails
- `GET /api/emails/` - List all emails (Gmail + .eml files)
- `GET /api/emails/<id>` - Get email raw HTML
- `POST /api/emails/<id>/star` - Mark email as starred
- `POST /api/emails/refresh` - Refresh email list

### Parse
- `GET /api/parse/<email_id>` - Parse an email
- `POST /api/parse/<email_id>/refresh` - Force re-parse

### Audio
- `POST /api/audio/chunk/<email_id>/<chunk_index>` - Generate audio for a chunk
- `POST /api/audio/generate` - Generate audio from SSML directly
- `GET /api/audio/file?path=...` - Serve cached audio file
- `POST /api/audio/cache/clear` - Clear audio cache

## Data Storage

- `dev_data/dev_storage.db` - PickleDB for state (starred emails, audio cache metadata)
- `dev_data/audio_cache/` - Cached audio files (keyed by SSML+voice hash)

## Development

The API runs in debug mode with auto-reload. Changes to the `email_exporter` code will be reflected after clicking "Refresh Parse" in the UI.
