import os
from openai import OpenAI

# --- Configuration ---
# This is the same client setup from sql_tutor.py
# Using OpenRouter to access various models
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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", # Hardcoded as requested
)
# You can change the model here if you want to test others
DEFAULT_MODEL = "openai/gpt-4"

def get_gpt_response(system_prompt, user_prompt, model):
    """Generic function to get a response from the language model."""
    print(f"\n--- Sending to model: {model} ---")
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

def get_multiline_input(prompt_message):
    """Reads multi-line input from the user until they enter 'DONE' on a new line."""
    print(f"\nEnter {prompt_message} (type 'DONE' on a new line when you're finished):")
    lines = []
    while True:
        try:
            line = input("> ")
            # Use .strip() to handle potential whitespace and case-insensitivity
            if line.strip().upper() == 'DONE':
                break
            if line.strip().upper() == 'QUIT':
                # Return a special value to signal quitting
                return 'quit'
            lines.append(line)
        except EOFError: # This handles Ctrl+D for Linux/macOS users
            break
    return "\n".join(lines)

def main():
    """Main loop to test prompts."""
    print("--- Prompt Engineering Tester ---")
    print("This tool now supports multi-line prompts.")
    print("Type 'quit' to exit at any prompt.")
    print("-" * 30)

    while True:
        system_prompt = get_multiline_input("SYSTEM prompt")
        if system_prompt == 'quit':
            break

        user_prompt = get_multiline_input("USER prompt")
        if user_prompt == 'quit':
            break
            
        model_to_use = input(f"\nEnter model name (or press Enter for default: {DEFAULT_MODEL}): \n> ").strip()
        if not model_to_use:
            model_to_use = DEFAULT_MODEL
        if model_to_use.lower() == 'quit':
            break

        response = get_gpt_response(system_prompt, user_prompt, model_to_use)

        print("\n" + "="*20 + " MODEL RESPONSE " + "="*20)
        print(response)
        print("="*58 + "\n")

if __name__ == "__main__":
    main() 