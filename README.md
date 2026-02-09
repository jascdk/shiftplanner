# shiftplanner

A Streamlit-based application to parse work rosters (PDF) using AI and sync them to Google Calendar. Designed to run in a Docker container on Proxmox.

## Features
- **PDF Parsing**: Extracts text from shift rosters.
- **AI Analysis**: Uses Google Gemini to structure unstructured text into JSON.
- **Calendar Sync**: Uploads shifts directly to Google Calendar.
- **Email Fetcher**: (Optional) Fetches the latest roster from your email via IMAP.

## Setup

### 1. Prerequisites
- **Google Cloud Credentials**: You need a `credentials.json` file for the Google Calendar API.
- **Gemini API Key**: Get one from Google AI Studio.

### 2. Local Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 3. Docker (Proxmox)
Build the image:
```bash
docker build -t shiftplanner .
```

Run the container (ensure you mount your credentials):
```bash
docker run -d -p 8501:8501 \
  -v $(pwd)/credentials.json:/app/credentials.json \
  -v $(pwd)/token.json:/app/token.json \
  shiftplanner
```
