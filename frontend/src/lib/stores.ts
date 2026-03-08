import { writable } from 'svelte/store';
import type { ProficiencyLevel, GenerateResponse, TemplateSummary } from './types';

// Current screen: 'landing' | 'configure' | 'loading' | 'results'
export const currentScreen = writable<string>('landing');

// Configuration form state
export const selectedTemplateId = writable<string | null>(null);
export const rubricMode = writable<'template' | 'custom'>('template');
export const customRubricText = writable<string>('');
export const assignmentPrompt = writable<string>('');
export const gradeLevel = writable<number>(8);
export const selectedLevels = writable<ProficiencyLevel[]>(['Below', 'Approaching', 'Proficient', 'Exemplary']);

// Results — keyed by proficiency level
export const results = writable<Record<string, GenerateResponse>>({});
export const errors = writable<Record<string, string>>({});

// Templates (loaded once)
export const templates = writable<TemplateSummary[]>([]);
