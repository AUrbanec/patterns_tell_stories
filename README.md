# Podcast Relationship Mapper

A web application that analyzes podcast audio using Gemini Pro 2.5 to extract entities, relationships, and create interactive knowledge graphs.

## Features

- **Audio Processing**: Splits podcast episodes into 5-minute chunks for analysis
- **AI Analysis**: Uses Google's Gemini 2.5 Pro to extract entities, relationships, and details
- **Knowledge Graph**: Interactive visualization using Cytoscape.js
- **Entity Management**: Tracks people, organizations, events, concepts, and source materials
- **Timestamp References**: Links all extracted information to specific audio timestamps
- **SQLite Database**: Stores all data with eventual PostgreSQL migration support

## Setup

### Prerequisites

- Python 3.8+
- Google AI API key (Gemini)
- Modern web browser

### Installation

1. **Clone and setup the backend:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set your Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# Initialize the database
python -c "from database import create_tables; create_tables()"
```

2. **Start the backend server:**
```bash
python main.py
# Server will run on http://localhost:8000
```

3. **Serve the frontend:**
```bash
# Option 1: Simple HTTP server
cd frontend
python -m http.server 3000

# Option 2: Using Node.js
npx serve frontend -p 3000

# Frontend will be available at http://localhost:3000
```

### API Key Setup

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and set it as an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

## Usage

### 1. Upload a Podcast Episode

1. Open the frontend at http://localhost:3000
2. Click "Upload New Episode"
3. Enter episode title and optional URL
4. Select your audio file (MP3, WAV, etc.)
5. Click "Upload and Process"

The system will:
- Split the audio into 5-minute chunks
- Send each chunk to Gemini for analysis
- Extract entities, relationships, and details
- Store everything in the database with timestamp references

### 2. View the Knowledge Graph

1. Select a processed episode from the dropdown
2. Click "Load Graph"
3. Explore the interactive network visualization
4. Click on nodes to see detailed information
5. View timestamp references for each piece of information

### 3. Entity Types

The system extracts and categorizes:
- **People**: Individuals mentioned in the podcast
- **Organizations**: Companies, institutions, groups
- **Events**: Specific occurrences, meetings, incidents
- **Concepts**: Ideas, theories, methodologies
- **Source Material**: Books, documents, studies referenced

## API Endpoints

### Episodes
- `POST /api/episodes` - Create new episode
- `GET /api/episodes` - List all episodes
- `POST /api/episodes/{id}/process` - Upload and process audio
- `GET /api/episodes/{id}/graph` - Get graph data for episode

### Entities
- `GET /api/entities/{id}/details` - Get entity details with timestamps

## Database Schema

### Tables
- **episodes**: Episode metadata and processing status
- **entities**: Master list of all people, organizations, etc.
- **details**: Specific facts about entities with source references
- **relationships**: Connections between entities
- **sources**: Audio chunks with timestamp ranges

## Architecture

```
Frontend (Static HTML/JS/CSS)
    ↓ HTTP API calls
Backend (FastAPI + Python)
    ↓ Audio processing
Gemini 2.5 Pro API
    ↓ Data storage
SQLite Database
```

## File Structure

```
├── main.py              # FastAPI application
├── database.py          # SQLAlchemy models and setup
├── audio_processor.py   # Audio chunking and Gemini integration
├── data_service.py      # Database operations
├── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html      # Main web interface
│   ├── styles.css      # Styling
│   └── app.js          # Frontend JavaScript
└── README.md           # This file
```

## Key Modifications from Original Plan

- **Chunk Duration**: Changed from 60 seconds to 5 minutes as requested
- **Audio Processing**: Uses Gemini's native audio processing instead of separate transcription
- **Frontend**: Simple vanilla JavaScript instead of complex framework
- **Database**: Ready for PostgreSQL migration with SQLAlchemy

## Future Enhancements

- Audio playback with timestamp jumping
- Advanced graph filtering and search
- Export capabilities (JSON, CSV)
- User authentication and multi-user support
- PostgreSQL migration for production
- Batch processing for multiple episodes
- Advanced entity disambiguation
- Integration with podcast RSS feeds

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY environment variable not set"**
   - Make sure you've exported your API key: `export GEMINI_API_KEY="your_key"`

2. **CORS errors in frontend**
   - Ensure the backend is running on port 8000
   - Check that the frontend is served via HTTP (not file://)

3. **Audio processing fails**
   - Verify your audio file format is supported (MP3, WAV, AAC, OGG, FLAC)
   - Check that the file isn't too large (Gemini has size limits)

4. **Graph doesn't load**
   - Ensure the episode has been fully processed (status: "complete")
   - Check browser console for JavaScript errors

## Contributing

This is an MVP implementation. Areas for improvement:
- Error handling and user feedback
- Performance optimization for large graphs
- Mobile responsiveness
- Accessibility features
- Unit tests and integration tests