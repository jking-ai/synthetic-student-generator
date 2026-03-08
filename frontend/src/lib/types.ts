export type ProficiencyLevel = 'Below' | 'Approaching' | 'Proficient' | 'Exemplary';

export const PROFICIENCY_LEVELS: ProficiencyLevel[] = ['Below', 'Approaching', 'Proficient', 'Exemplary'];

export const LEVEL_COLORS: Record<ProficiencyLevel, string> = {
  Below: 'var(--color-below)',
  Approaching: 'var(--color-approaching)',
  Proficient: 'var(--color-proficient)',
  Exemplary: 'var(--color-exemplary)'
};

export const LEVEL_BG_CLASSES: Record<ProficiencyLevel, string> = {
  Below: 'bg-red-500',
  Approaching: 'bg-amber-500',
  Proficient: 'bg-green-500',
  Exemplary: 'bg-blue-500'
};

export const LEVEL_TEXT_CLASSES: Record<ProficiencyLevel, string> = {
  Below: 'text-red-600',
  Approaching: 'text-amber-600',
  Proficient: 'text-green-600',
  Exemplary: 'text-blue-600'
};

export interface TemplateSummary {
  id: string;
  name: string;
  description: string;
  grade_range: string;
  dimensions: string[];
}

export interface RubricDimensionLevel {
  Exemplary: string;
  Proficient: string;
  Approaching: string;
  Below: string;
}

export interface RubricDimension {
  name: string;
  levels: RubricDimensionLevel;
}

export interface TemplateDetail extends TemplateSummary {
  dimensions: RubricDimension[] | string[];
}

export interface PersonaNotes {
  grade_level: number;
  overall_level: string;
  writing_strengths: string[];
  writing_weaknesses: string[];
  error_patterns_applied: string[];
}

export interface WritingTraits {
  word_count: number;
  paragraph_count: number;
  average_sentence_length: number;
  tone: string;
}

export interface GeneratedSample {
  student_response: string;
  proficiency_scores: Record<string, string>;
  persona_notes: PersonaNotes;
  writing_traits: WritingTraits;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  thinking_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
}

export interface GenerationMetadata {
  model: string;
  generation_time_ms: number;
  template_used: string | null;
  request_id: string;
  token_usage: TokenUsage | null;
}

export interface GenerateResponse {
  sample: GeneratedSample;
  metadata: GenerationMetadata;
}
