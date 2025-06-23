"""
AI service for handling language model interactions.
"""

import json
from typing import Optional, Dict, Any
from config.settings import CLIENT, MODEL


class AIService:
    """Service for handling AI/LLM interactions."""
    
    @staticmethod
    def get_response(system_prompt: str, user_prompt: str, json_mode: bool = False) -> Optional[str]:
        """Get a response from the language model."""
        print("\n🧠 Agent is thinking...")
        try:
            response_kwargs = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            if json_mode:
                response_kwargs["response_format"] = {"type": "json_object"}

            response = CLIENT.chat.completions.create(**response_kwargs)
            content = response.choices[0].message.content
            print("✅ Agent responded.")
            return content
        except Exception as e:
            print(f"\n[Error: Could not get AI response. Reason: {e}]")
            return None
    
    @staticmethod
    def parse_json_response(response_str: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from AI and handle errors gracefully."""
        if not response_str:
            return None
            
        try:
            return json.loads(response_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing AI JSON response: {e}")
            print("Raw response:", response_str)
            return None 