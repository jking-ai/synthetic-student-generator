const BASE = '';  // Uses Vite proxy in dev, Firebase rewrite in prod

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/api/v1/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function getTemplates() {
  const res = await fetch(`${BASE}/api/v1/templates`);
  if (!res.ok) throw new Error('Failed to load templates');
  return res.json();
}

export async function getTemplate(id: string) {
  const res = await fetch(`${BASE}/api/v1/templates/${id}`);
  if (!res.ok) throw new Error('Template not found');
  return res.json();
}

export interface GenerateParams {
  assignment_prompt: string;
  proficiency_level: string;
  template_id?: string;
  rubric?: object;
  rubric_text?: string;
  grade_level: number;
}

export async function generate(params: GenerateParams) {
  const res = await fetch(`${BASE}/api/v1/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: 'Generation failed' } }));
    throw new Error(err.error?.message || 'Generation failed');
  }
  return res.json();
}
