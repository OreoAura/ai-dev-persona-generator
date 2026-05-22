# AI Dev Persona Generator

This is a FastAPI backend that:
- Fetches GitHub user data
- Uses Gemini AI to analyze developer persona
- Returns a fun developer profile card

## Features
- GitHub API integration
- Google Gemini AI analysis
- HTML profile card generation
- Deployed on Google Cloud Run

## Endpoints
- /health → Health check
- /github/{username} → GitHub data
- /analyze/{username} → AI analysis
- /card/{username} → HTML profile card

## Tech Stack
- Python
- FastAPI
- Google Gemini AI
- Cloud Run