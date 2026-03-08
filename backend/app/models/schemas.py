"""Gemini response schema for structured output.

This dict is passed to Gemini's response_schema parameter to constrain
the JSON output to match the GeneratedSample structure.
"""

GENERATED_SAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "student_response": {
            "type": "string",
            "description": "The complete student-written response to the assignment.",
        },
        "proficiency_scores": {
            "type": "object",
            "description": "A mapping of each rubric dimension name to the proficiency level targeted (Below, Approaching, Proficient, or Exemplary).",
            "additionalProperties": {"type": "string"},
        },
        "persona_notes": {
            "type": "object",
            "description": "Metadata about the student persona used for generation.",
            "properties": {
                "grade_level": {"type": "integer"},
                "overall_level": {
                    "type": "string",
                    "enum": ["Below", "Approaching", "Proficient", "Exemplary"],
                },
                "writing_strengths": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "writing_weaknesses": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "error_patterns_applied": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "grade_level",
                "overall_level",
                "writing_strengths",
                "writing_weaknesses",
                "error_patterns_applied",
            ],
        },
        "writing_traits": {
            "type": "object",
            "description": "Quantitative traits of the generated writing sample.",
            "properties": {
                "word_count": {"type": "integer"},
                "paragraph_count": {"type": "integer"},
                "average_sentence_length": {"type": "number"},
                "tone": {"type": "string"},
            },
            "required": [
                "word_count",
                "paragraph_count",
                "average_sentence_length",
                "tone",
            ],
        },
    },
    "required": [
        "student_response",
        "proficiency_scores",
        "persona_notes",
        "writing_traits",
    ],
}
