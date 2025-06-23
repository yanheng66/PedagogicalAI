"""
Input/Output helper functions for user interaction.
"""

import sys
from config.settings import EXIT_COMMANDS, HEADER_SEPARATOR


def get_user_input(prompt: str) -> str:
    """Get user input and handle exit command."""
    response = input(prompt).strip()
    if response.lower() in EXIT_COMMANDS:
        print("\n👋 Exiting the agent.")
        sys.exit(0)
    return response


def print_header(title: str) -> None:
    """Prints a formatted header for each step."""
    print("\n" + HEADER_SEPARATOR)
    print(f"🔹 {title}")
    print(HEADER_SEPARATOR) 