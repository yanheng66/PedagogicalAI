"""
Configuration settings for the SQL Tutor application.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # Loads environment variables from a .env file if it exists

# --- API Configuration ---
# Load the OpenRouter API key from environment variables
# IMPORTANT: Create a .env file in the root directory and add your key:
# OPENROUTER_API_KEY="your-secret-key-here"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables. Please set it in your .env file.")

CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)
MODEL = "openai/gpt-4o-mini"

# --- Application Constants ---
EXIT_COMMANDS = ['quit', 'exit']
HEADER_SEPARATOR = "=" * 60 