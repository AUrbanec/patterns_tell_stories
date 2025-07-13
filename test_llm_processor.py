import unittest
import os
from unittest.mock import patch, MagicMock
from llm_processor import LLMProcessor
from audio_processor import AudioProcessor
from data_service import DataService
from database import create_tables, get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

class TestLLMProcessor(unittest.TestCase):

    def setUp(self):
        # Set up the in-memory database
        Base.metadata.create_all(bind=engine)
        self.db = next(override_get_db())
        self.data_service = DataService(self.db)

    def tearDown(self):
        # Tear down the in-memory database
        Base.metadata.drop_all(bind=engine)
        self.db.close()

    @patch('llm_processor.genai.GenerativeModel')
    def test_refine_relationship_map(self, mock_generative_model):
        # Mock the response from the LLM
        mock_response = MagicMock()
        mock_response.text = '''
```json
{
  "entities": [
    {"name": "Test Entity", "type": "Person", "summary": "A test entity."}
  ],
  "relationships": [],
  "details": [
    {"entity": "Test Entity", "detail": "A detail about the test entity."}
  ]
}
```
'''
        mock_generative_model.return_value.generate_content.return_value = mock_response

        # Sample chunks data
        chunks = [
            {
                "analysis": {
                    "entities": [{"name": "Test Entity", "type": "Person", "summary": "A test entity."}],
                    "relationships": [],
                    "details": [{"entity": "Test Entity", "detail": "A detail about the test entity."}]
                }
            }
        ]

        # Initialize the LLMProcessor and call the method
        llm_processor = LLMProcessor(gemini_api_key="test_key")
        refined_data = llm_processor.refine_relationship_map(chunks)

        # Assert that the data is refined as expected
        self.assertIn("entities", refined_data)
        self.assertEqual(len(refined_data["entities"]), 1)
        self.assertEqual(refined_data["entities"][0]["name"], "Test Entity")

    @patch('audio_processor.AudioProcessor.analyze_audio_chunk')
    @patch('llm_processor.LLMProcessor.refine_relationship_map')
    def test_audio_processor_integration(self, mock_refine_relationship_map, mock_analyze_audio_chunk):
        # Mock the analysis of audio chunks
        mock_analyze_audio_chunk.return_value = {
            "entities": [{"name": "Chunk Entity", "type": "Person", "summary": "A chunk entity."}],
            "relationships": [],
            "details": []
        }

        # Mock the refined analysis from the LLMProcessor
        mock_refine_relationship_map.return_value = {
            "entities": [{"name": "Refined Entity", "type": "Person", "summary": "A refined entity."}],
            "relationships": [],
            "details": []
        }

        # Initialize the AudioProcessor and process a dummy audio file
        audio_processor = AudioProcessor(gemini_api_key="test_key")

        # Mock the split_audio_into_chunks to return a single dummy chunk
        with patch.object(audio_processor, 'split_audio_into_chunks', return_value=['dummy_chunk.mp3']) as mock_split:
            refined_analysis = audio_processor.process_full_audio("dummy_path.mp3", episode_id=1)

            # Assert that the refined analysis is returned
            self.assertIn("analysis", refined_analysis)
            self.assertEqual(len(refined_analysis["analysis"]["entities"]), 1)
            self.assertEqual(refined_analysis["analysis"]["entities"][0]["name"], "Refined Entity")

if __name__ == '__main__':
    unittest.main()
