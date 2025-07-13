#!/usr/bin/env python3
"""
Debug script to test a single audio chunk analysis
"""
import os
from audio_processor import AudioProcessor

def test_analysis():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    processor = AudioProcessor(api_key)
    
    # Create a simple test audio file (you can replace this with a real file path)
    print("Testing audio analysis...")
    print("Note: Replace 'test_audio.mp3' with an actual audio file path")
    
    # For now, let's just test the prompt structure
    print("Prompt structure looks good. To test with real audio:")
    print("1. Place a short audio file in the project directory")
    print("2. Update this script with the file path")
    print("3. Run: python debug_analysis.py")

if __name__ == "__main__":
    test_analysis()