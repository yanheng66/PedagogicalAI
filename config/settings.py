"""
Configuration settings for the SQL Tutor application.
"""

from openai import OpenAI

# --- API Configuration ---
# API key is hardcoded as requested for this testing version.
# CLIENT = OpenAI(api_key="sk-你的官方key")  # 不要 base_url
# OpenRouter（需要有效 key）
# CLIENT = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="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",
# )
# MODEL = "microsoft/wizardlm-2-8x22b"

# OpenAI 官方（如果你有官方 key）
CLIENT = OpenAI(
    api_key="sk-你的OpenAI官方key"  # 替换为你的真实 key
)
MODEL = "gpt-3.5-turbo"

# --- Application Constants ---
EXIT_COMMANDS = ['quit', 'exit']
HEADER_SEPARATOR = "=" * 60 