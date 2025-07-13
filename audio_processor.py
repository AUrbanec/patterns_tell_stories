import os
from pydub import AudioSegment
import google.generativeai as genai
import json
from typing import List, Dict, Any
import tempfile

class AudioProcessor:
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model_name='gemini-2.5-pro')
        
    def split_audio_into_chunks(self, audio_file_path: str, chunk_duration_minutes: int = 5) -> List[str]:
        """
        Split audio file into chunks of specified duration (default 5 minutes).
        Returns list of temporary file paths for each chunk.
        """
        audio = AudioSegment.from_file(audio_file_path)
        chunk_duration_ms = chunk_duration_minutes * 60 * 1000  # Convert to milliseconds
        
        chunks = []
        chunk_files = []
        
        # Split audio into chunks
        for i in range(0, len(audio), chunk_duration_ms):
            chunk = audio[i:i + chunk_duration_ms]
            chunks.append(chunk)
        
        # Save chunks to temporary files
        for i, chunk in enumerate(chunks):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            chunk.export(temp_file.name, format="mp3")
            chunk_files.append(temp_file.name)
            temp_file.close()
        
        return chunk_files
    
    def analyze_audio_chunk(self, audio_chunk_path: str) -> Dict[str, Any]:
        """
        Analyze a single audio chunk using Gemini 2.5 Pro.
        Returns structured data about entities, relationships, and details.
        """
        try:
            # Upload the audio chunk to Gemini Files API
            print(f"Uploading audio chunk: {audio_chunk_path}")
            audio_file = genai.files.upload_file(
                path=audio_chunk_path,
                display_name=os.path.basename(audio_chunk_path)
            )
            print(f"Completed upload: {audio_file.uri}")
            
            # Construct the prompt
            prompt_parts = [
                "You are a meticulous research analyst building a knowledge graph from a podcast.",
                "Analyze the provided audio file. Extract all entities (people, organizations, events, concepts, source material) and the relationships between them.",
                "For each entity, provide its canonical name and type.",
                "For each relationship, describe the link between a source entity and a target entity.",
                "For each key detail about an entity, describe it.",
                "Return your findings ONLY as a JSON object with the following structure:",
                """
                {
                  "entities": [
                    {"name": "Entity Name", "type": "Person|Organization|Event|Concept|Source Material", "summary": "A brief description."}
                  ],
                  "relationships": [
                    {"source": "Source Entity Name", "target": "Target Entity Name", "description": "Description of the relationship."}
                  ],
                  "details": [
                    {"entity": "Entity Name", "detail": "The specific detail about this entity."}
                  ]
                }
                """,
                audio_file
            ]
            
            # Generate content
            print("Generating content from audio...")
            response = self.model.generate_content(prompt_parts)
            
            # Parse JSON response
            try:
                analysis_data = json.loads(response.text)
                return analysis_data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Raw response: {response.text}")
                return {"entities": [], "relationships": [], "details": []}
                
        except Exception as e:
            print(f"Error analyzing audio chunk: {e}")
            return {"entities": [], "relationships": [], "details": []}
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """Clean up temporary audio chunk files."""
        for file_path in file_paths:
            try:
                os.unlink(file_path)
            except OSError:
                pass
    
    def process_full_audio(self, audio_file_path: str, episode_id: int) -> List[Dict[str, Any]]:
        """
        Process a complete audio file by splitting into chunks and analyzing each.
        Returns list of analysis results with timing information.
        """
        chunk_files = self.split_audio_into_chunks(audio_file_path, chunk_duration_minutes=5)
        results = []
        
        try:
            for i, chunk_file in enumerate(chunk_files):
                start_time = i * 5 * 60  # 5 minutes in seconds
                end_time = (i + 1) * 5 * 60
                
                print(f"Processing chunk {i+1}/{len(chunk_files)} ({start_time}s - {end_time}s)")
                
                analysis = self.analyze_audio_chunk(chunk_file)
                
                # Add timing information
                result = {
                    "episode_id": episode_id,
                    "timestamp_start": start_time,
                    "timestamp_end": end_time,
                    "analysis": analysis
                }
                results.append(result)
                
        finally:
            # Clean up temporary files
            self.cleanup_temp_files(chunk_files)
        
        return results