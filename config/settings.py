"""
Configuration settings for the SQL Tutor application.
"""

from openai import OpenAI

# --- API Configuration ---
# API key is hardcoded as requested for this testing version.
CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

MODEL = "openai/gpt-4"

# --- Application Constants ---
EXIT_COMMANDS = ['quit', 'exit']
HEADER_SEPARATOR = "=" * 60 