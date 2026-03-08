from pathlib import Path


_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "persona_template.txt"
_PERSONA_TEMPLATE: str | None = None


def _load_template() -> str:
    global _PERSONA_TEMPLATE
    if _PERSONA_TEMPLATE is None:
        _PERSONA_TEMPLATE = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return _PERSONA_TEMPLATE


def build_system_instruction(
    rubric_detail: dict,
    proficiency_level: str,
    grade_level: int,
    persona_config: dict | None = None,
) -> str:
    """Build the full system instruction for Gemini.

    Args:
        rubric_detail: A rubric dict with "dimensions" list, each having
            "name" and "levels" (dict with Exemplary/Proficient/Approaching/Below).
        proficiency_level: The target proficiency level string.
        grade_level: The student's grade level (3-12).
        persona_config: Optional dict with "error_patterns" and "voice_traits" lists.

    Returns:
        The fully populated system instruction string.
    """
    # Build rubric dimensions block
    dimensions_lines: list[str] = []
    for dim in rubric_detail.get("dimensions", []):
        name = dim["name"]
        levels = dim["levels"]
        target_descriptor = levels.get(proficiency_level, "N/A")
        dimensions_lines.append(f"### {name}")
        dimensions_lines.append(f"  Target level ({proficiency_level}): {target_descriptor}")
        dimensions_lines.append(f"  - Exemplary: {levels.get('Exemplary', 'N/A')}")
        dimensions_lines.append(f"  - Proficient: {levels.get('Proficient', 'N/A')}")
        dimensions_lines.append(f"  - Approaching: {levels.get('Approaching', 'N/A')}")
        dimensions_lines.append(f"  - Below: {levels.get('Below', 'N/A')}")
        dimensions_lines.append("")

    rubric_dimensions = "\n".join(dimensions_lines)

    # Build optional sections
    error_patterns_section = ""
    voice_traits_section = ""

    if persona_config:
        patterns = persona_config.get("error_patterns", [])
        traits = persona_config.get("voice_traits", [])

        if patterns:
            error_patterns_section = (
                f"INTENTIONAL ERROR PATTERNS TO INCLUDE: {', '.join(patterns)}"
            )
        if traits:
            voice_traits_section = (
                f"VOICE AND STYLE TRAITS: {', '.join(traits)}"
            )

    template = _load_template()
    return template.format(
        grade_level=grade_level,
        proficiency_level=proficiency_level,
        rubric_dimensions=rubric_dimensions,
        error_patterns_section=error_patterns_section,
        voice_traits_section=voice_traits_section,
    )


def build_user_prompt(assignment_prompt: str) -> str:
    """Wrap the assignment prompt in student-facing framing.

    Args:
        assignment_prompt: The teacher's assignment instructions.

    Returns:
        The user prompt string for Gemini.
    """
    return (
        "Here is the assignment your teacher gave you. "
        "Write your response as instructed.\n\n"
        f"ASSIGNMENT:\n{assignment_prompt}"
    )
