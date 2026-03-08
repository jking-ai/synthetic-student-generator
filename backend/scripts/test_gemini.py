"""Simple test script to verify Gemini connectivity and basic generation."""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.gemini_client import generate, GenerationError


def main():
    print("Testing Gemini connection...")
    print()

    schema = {
        "type": "object",
        "properties": {
            "greeting": {"type": "string"},
        },
        "required": ["greeting"],
    }

    try:
        result = generate(
            system_instruction="You are a friendly assistant. Respond with a one-sentence greeting.",
            user_prompt="Hello! Please greet me.",
            response_schema=schema,
        )
        print("Response received successfully!")
        print(f"Greeting: {result['greeting']}")
        print()
        print("Structured output confirmed working.")
    except GenerationError as exc:
        print(f"Generation failed: {exc}")
        if exc.cause:
            print(f"Cause: {exc.cause}")
        sys.exit(1)


if __name__ == "__main__":
    main()
