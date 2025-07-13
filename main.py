import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import tempfile
import shutil

from database import create_tables, get_db
from audio_processor import AudioProcessor
from data_service import DataService

app = FastAPI(title="Podcast Relationship Mapper", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a simple test endpoint
@app.get("/test")
async def test():
    return {"message": "API is working!", "status": "ok"}

# Initialize database
create_tables()

# Initialize audio processor (requires GEMINI_API_KEY environment variable)
def get_audio_processor():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set")
    return AudioProcessor(api_key)

@app.get("/")
async def root():
    return {"message": "Podcast Relationship Mapper API"}

@app.post("/api/episodes")
async def create_episode(title: str = Form(...), episode_url: str = Form(None), db: Session = Depends(get_db)):
    """Create a new episode record."""
    data_service = DataService(db)
    episode = data_service.create_episode(title, episode_url)
    return {"episode_id": episode.id, "title": episode.title, "status": episode.status}

@app.post("/api/episodes/{episode_id}/process")
async def process_episode_audio(
    episode_id: int,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process an audio file for an episode."""
    data_service = DataService(db)
    audio_processor = get_audio_processor()
    
    # Update episode status to processing
    data_service.update_episode_status(episode_id, "processing")
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            shutil.copyfileobj(audio_file.file, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Process the audio file
            analysis_results = audio_processor.process_full_audio(temp_file_path, episode_id)
            
            # Store results in database
            for result in analysis_results:
                data_service.process_analysis_chunk(result)
            
            # Update episode status to complete
            data_service.update_episode_status(episode_id, "complete")
            
            return {
                "message": f"Successfully processed {len(analysis_results)} audio chunks",
                "chunks_processed": len(analysis_results)
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        # Update episode status to failed
        data_service.update_episode_status(episode_id, "failed")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.get("/api/episodes/{episode_id}/graph")
async def get_episode_graph(episode_id: int, db: Session = Depends(get_db)):
    """Get graph data (nodes and edges) for an episode."""
    data_service = DataService(db)
    graph_data = data_service.get_episode_graph_data(episode_id)
    return graph_data

@app.get("/api/entities/{entity_id}/details")
async def get_entity_details(entity_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific entity."""
    data_service = DataService(db)
    entity_details = data_service.get_entity_details(entity_id)
    
    if not entity_details:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return entity_details

@app.get("/api/episodes")
async def list_episodes(db: Session = Depends(get_db)):
    """List all episodes."""
    from database import Episode
    episodes = db.query(Episode).all()
    return [
        {
            "id": ep.id,
            "title": ep.title,
            "episode_url": ep.episode_url,
            "status": ep.status,
            "processed_at": ep.processed_at
        }
        for ep in episodes
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)