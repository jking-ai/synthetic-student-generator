# Local Testing Guide

How to run tests, test the API manually, and verify frontend behavior.

---

## 1. Backend Tests

<!-- TODO: Add test commands once test suite is created -->

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_generate.py

# Run with coverage
pytest --cov=app
```

### Test Structure

<!-- TODO: Document test classes and what they cover -->
<!-- Expected test areas: prompt builder, generate endpoint, template loading, Pydantic validation -->

---

## 2. API Testing (curl examples)

<!-- TODO: Update curl examples once endpoints are implemented -->

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### List Templates

```bash
curl http://localhost:8000/api/v1/templates
```

### Generate a Sample (using template)

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_prompt": "Write a persuasive essay about school uniforms.",
    "proficiency_level": "Proficient",
    "template_id": "6-trait-writing",
    "grade_level": 8
  }'
```

### Generate a Sample (using custom rubric)

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_prompt": "Describe a time you faced a challenge.",
    "proficiency_level": "Approaching",
    "rubric": {
      "name": "Narrative Rubric",
      "dimensions": [
        {
          "name": "Story Structure",
          "levels": {
            "Exemplary": "Clear narrative arc with purposeful pacing.",
            "Proficient": "Contains all narrative elements.",
            "Approaching": "Some elements present but uneven.",
            "Below": "No discernible structure."
          }
        }
      ]
    },
    "grade_level": 6
  }'
```

---

## 3. Frontend Testing

<!-- TODO: Add frontend test commands once test framework is configured -->

```bash
cd frontend

# Run tests (Vitest)
npm test

# Run with watch mode
npm run test:watch
```

---

## 4. Manual Testing

<!-- TODO: Add manual testing checklist -->

### Generate Endpoint Validation

- [ ] Generate samples at each proficiency level (Below, Approaching, Proficient, Exemplary)
- [ ] Verify proficiency levels are distinguishable in output quality
- [ ] Test with each bundled rubric template
- [ ] Test with a custom rubric
- [ ] Verify error handling for invalid requests (missing rubric, invalid proficiency level)

### Frontend Validation

- [ ] Template selector populates from API
- [ ] Form submission shows loading state
- [ ] Generated sample displays with metadata
- [ ] Error states display correctly
