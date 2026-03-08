"""Test script to verify structured output generation with rubric and assignment prompt."""

import json
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.responses import GeneratedSample
from app.models.schemas import GENERATED_SAMPLE_SCHEMA
from app.services.gemini_client import generate, GenerationError
from app.services.prompt_builder import build_system_instruction, build_user_prompt


# Hardcoded test rubric
TEST_RUBRIC = {
    "name": "Test Rubric",
    "dimensions": [
        {
            "name": "Ideas",
            "levels": {
                "Exemplary": "Writing is clear, focused, and richly developed with specific details.",
                "Proficient": "Writing is clear and focused with adequate development.",
                "Approaching": "Writing attempts to address the topic but development is limited.",
                "Below": "Writing lacks a clear central idea or purpose.",
            },
        },
        {
            "name": "Organization",
            "levels": {
                "Exemplary": "Structure enhances the central idea with smooth transitions.",
                "Proficient": "Writing has a recognizable structure with clear beginning, middle, and end.",
                "Approaching": "An attempt at organization is evident but inconsistent.",
                "Below": "Writing lacks a clear organizational structure.",
            },
        },
    ],
}

TEST_ASSIGNMENT = (
    "Write a short essay about your favorite season and explain why you like it. "
    "Include at least two reasons with supporting details."
)


def main():
    print("Testing structured output generation...")
    print(f"Proficiency level: Approaching")
    print(f"Grade level: 7")
    print()

    system_instruction = build_system_instruction(
        rubric_detail=TEST_RUBRIC,
        proficiency_level="Approaching",
        grade_level=7,
        persona_config={
            "error_patterns": ["run-on sentences", "inconsistent capitalization"],
            "voice_traits": ["uses filler words", "informal tone"],
        },
    )
    user_prompt = build_user_prompt(TEST_ASSIGNMENT)

    print("System instruction (first 200 chars):")
    print(system_instruction[:200] + "...")
    print()

    try:
        raw_response = generate(
            system_instruction=system_instruction,
            user_prompt=user_prompt,
            response_schema=GENERATED_SAMPLE_SCHEMA,
        )

        print("Raw response received. Parsing into GeneratedSample...")
        sample = GeneratedSample(**raw_response)

        print()
        print("=" * 60)
        print("GENERATED SAMPLE")
        print("=" * 60)
        print()
        print("Student Response:")
        print("-" * 40)
        print(sample.student_response)
        print()
        print("Proficiency Scores:")
        for dim, score in sample.proficiency_scores.items():
            print(f"  {dim}: {score}")
        print()
        print("Persona Notes:")
        print(f"  Grade Level: {sample.persona_notes.grade_level}")
        print(f"  Overall Level: {sample.persona_notes.overall_level}")
        print(f"  Strengths: {sample.persona_notes.writing_strengths}")
        print(f"  Weaknesses: {sample.persona_notes.writing_weaknesses}")
        print(f"  Error Patterns: {sample.persona_notes.error_patterns_applied}")
        print()
        print("Writing Traits:")
        print(f"  Word Count: {sample.writing_traits.word_count}")
        print(f"  Paragraph Count: {sample.writing_traits.paragraph_count}")
        print(f"  Avg Sentence Length: {sample.writing_traits.average_sentence_length}")
        print(f"  Tone: {sample.writing_traits.tone}")
        print()
        print("All fields present and valid. Structured output test PASSED.")

    except GenerationError as exc:
        print(f"Generation failed: {exc}")
        if exc.cause:
            print(f"Cause: {exc.cause}")
        sys.exit(1)
    except Exception as exc:
        print(f"Validation/parsing failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
