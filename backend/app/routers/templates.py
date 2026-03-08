import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.responses import TemplateSummary, TemplatesListResponse

router = APIRouter()

_TEMPLATES_PATH = Path(__file__).resolve().parent.parent / "data" / "rubric_templates.json"
_templates: list[dict] | None = None


def _load_templates() -> list[dict]:
    global _templates
    if _templates is None:
        _templates = json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    return _templates


@router.get("/templates", response_model=TemplatesListResponse)
async def list_templates() -> TemplatesListResponse:
    templates = _load_templates()
    summaries = [
        TemplateSummary(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            grade_range=t["grade_range"],
            dimensions=[d["name"] for d in t["dimensions"]],
        )
        for t in templates
    ]
    return TemplatesListResponse(templates=summaries)


@router.get("/templates/{template_id}")
async def get_template(template_id: str) -> dict:
    templates = _load_templates()
    for t in templates:
        if t["id"] == template_id:
            return t
    raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
