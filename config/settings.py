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