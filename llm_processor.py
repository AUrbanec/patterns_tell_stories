import google.generativeai as genai
import json
import re
from typing import List, Dict, Any

class LLMProcessor:
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest')

    def refine_relationship_map(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Refine the relationship map from a list of chunks using an LLM.
        """
        # Combine the analysis from all chunks into one large data structure
        combined_analysis = {"entities": [], "relationships": [], "details": []}
        for chunk in chunks:
            analysis = chunk.get("analysis", {})
            if "entities" in analysis:
                combined_analysis["entities"].extend(analysis["entities"])
            if "relationships" in analysis:
                combined_analysis["relationships"].extend(analysis["relationships"])
            if "details" in analysis:
                combined_analysis["details"].extend(analysis["details"])

        # Create a prompt for the LLM to refine the data
        prompt = self.construct_refinement_prompt(combined_analysis)

        # Call the LLM to get the refined data
        refined_data = self.get_refined_data(prompt)

        return refined_data

    def construct_refinement_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """
        Construct the prompt for the LLM to refine the relationship map.
        """
        # Convert the analysis data to a JSON string
        json_data_str = json.dumps(analysis_data, indent=2)

        prompt = (
            "You are a data analyst tasked with refining a knowledge graph from a podcast. "
            "The following JSON data contains entities, relationships, and details extracted from different chunks of the podcast. "
            "Your task is to consolidate this information, remove duplicates, and ensure consistency. "
            "Please return a single, refined JSON object with the final relationship map.\n\n"
            f"Here is the data:\n{json_data_str}\n\n"
            "Please provide the refined data in the following format:\n"
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
            """
        )
        return prompt

    def get_refined_data(self, prompt: str) -> Dict[str, Any]:
        """
        Get the refined data from the LLM.
        """
        try:
            response = self.model.generate_content([prompt])
            # Attempt to find the JSON block in the response
            json_match = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.text

            refined_data = json.loads(json_str)
            return refined_data
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error getting refined data: {e}")
            return {"entities": [], "relationships": [], "details": []}
