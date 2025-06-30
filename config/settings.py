"""
Configuration settings for the SQL Tutor application.
"""

from openai import OpenAI

# --- API Configuration ---
# OpenRouter（使用用户提供的有效密钥）
CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)
MODEL = "mistralai/mistral-7b-instruct"

# --- Application Constants ---
EXIT_COMMANDS = ['quit', 'exit']
HEADER_SEPARATOR = "=" * 60 