<script lang="ts">
  import { get } from 'svelte/store';
  import {
    currentScreen,
    results,
    errors,
    selectedLevels,
    assignmentPrompt,
    gradeLevel,
    rubricMode,
    selectedTemplateId,
    customRubricText
  } from '$lib/stores';
  import {
    PROFICIENCY_LEVELS,
    LEVEL_BG_CLASSES,
    type ProficiencyLevel,
    type GenerateResponse
  } from '$lib/types';
  import { generate } from '$lib/api';

  let activeTab = $state<ProficiencyLevel>('Proficient');
  let copyFeedback = $state<string | null>(null);
  let retryingLevel = $state<ProficiencyLevel | null>(null);

  // Subscribe reactively to stores
  let resultMap: Record<string, GenerateResponse> = $state({});
  let errorMap: Record<string, string> = $state({});
  let selectedLevelsList: ProficiencyLevel[] = $state([]);

  results.subscribe(v => { resultMap = v; });
  errors.subscribe(v => { errorMap = v; });
  selectedLevels.subscribe(v => { selectedLevelsList = v; });

  // Only show tabs for levels that have results or errors
  const levels = $derived(
    PROFICIENCY_LEVELS.filter(l =>
      selectedLevelsList.includes(l) && (resultMap[l] || errorMap[l])
    )
  );

  // Set initial active tab to first available level
  $effect(() => {
    if (levels.length > 0 && !levels.includes(activeTab)) {
      activeTab = levels[0];
    }
  });

  const activeResult = $derived(resultMap[activeTab] as GenerateResponse | undefined);
  const activeError = $derived(errorMap[activeTab] as string | undefined);

  const tabColors: Record<ProficiencyLevel, { active: string; inactive: string; border: string }> = {
    Below: { active: 'bg-red-50 text-red-700', inactive: 'text-red-400 hover:text-red-600', border: 'border-red-500' },
    Approaching: { active: 'bg-amber-50 text-amber-700', inactive: 'text-amber-400 hover:text-amber-600', border: 'border-amber-500' },
    Proficient: { active: 'bg-green-50 text-green-700', inactive: 'text-green-400 hover:text-green-600', border: 'border-green-500' },
    Exemplary: { active: 'bg-blue-50 text-blue-700', inactive: 'text-blue-400 hover:text-blue-600', border: 'border-blue-500' }
  };

  async function copyText(text: string, label: string) {
    try {
      await navigator.clipboard.writeText(text);
      copyFeedback = label;
      setTimeout(() => { copyFeedback = null; }, 2000);
    } catch {
      copyFeedback = 'Copy failed';
      setTimeout(() => { copyFeedback = null; }, 2000);
    }
  }

  function copyCurrent() {
    if (activeResult) {
      copyText(activeResult.sample.student_response, 'Copied!');
    }
  }

  function copyAll() {
    const parts: string[] = [];
    for (const level of levels) {
      const r = resultMap[level];
      if (r) {
        parts.push(`=== ${level} ===\n\n${r.sample.student_response}`);
      }
    }
    copyText(parts.join('\n\n---\n\n'), 'All copied!');
  }

  function startOver() {
    currentScreen.set('landing');
    results.set({});
    errors.set({});
    assignmentPrompt.set('');
    selectedTemplateId.set(null);
    customRubricText.set('');
    rubricMode.set('template');
    gradeLevel.set(8);
    selectedLevels.set(['Below', 'Approaching', 'Proficient', 'Exemplary']);
  }

  async function retryLevel(level: ProficiencyLevel) {
    retryingLevel = level;

    const prompt = get(assignmentPrompt);
    const grade = get(gradeLevel);
    const mode = get(rubricMode);
    const templateId = get(selectedTemplateId);
    const rubricText = get(customRubricText);

    const params: Record<string, unknown> = {
      assignment_prompt: prompt,
      proficiency_level: level,
      grade_level: grade
    };

    if (mode === 'template' && templateId) {
      params.template_id = templateId;
    } else if (mode === 'custom' && rubricText) {
      params.rubric_text = rubricText;
    }

    try {
      const res = await generate(params as any);
      results.update((current) => ({ ...current, [level]: res }));
      errors.update((current) => {
        const next = { ...current };
        delete next[level];
        return next;
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Generation failed';
      errors.update((current) => ({ ...current, [level]: msg }));
    } finally {
      retryingLevel = null;
    }
  }

  function editAndRegenerate() {
    currentScreen.set('configure');
  }
</script>

<div class="mx-auto max-w-4xl px-6 py-8">
  <div class="flex items-center justify-between">
    <h2 class="text-2xl font-bold text-gray-900">Generated Samples</h2>
    <div class="flex items-center gap-2">
      {#if copyFeedback}
        <span class="text-sm font-medium text-green-600">{copyFeedback}</span>
      {/if}
      <span class="text-sm text-gray-400">{levels.length} sample{levels.length !== 1 ? 's' : ''}</span>
    </div>
  </div>

  <!-- Level Selector -->
  <div class="mt-6 grid grid-cols-2 gap-2 sm:flex sm:gap-1 sm:border-b sm:border-gray-200">
    {#each levels as level}
      <button
        onclick={() => { activeTab = level; }}
        class="flex items-center justify-center gap-2 rounded-lg border-2 px-4 py-2.5 text-sm font-medium transition sm:justify-start sm:rounded-none sm:border-0 sm:border-b-2 {activeTab === level ? `${tabColors[level].active} ${tabColors[level].border}` : `border-transparent bg-gray-50 sm:bg-transparent ${tabColors[level].inactive}`}"
      >
        <span class="h-2.5 w-2.5 rounded-full {LEVEL_BG_CLASSES[level]}"></span>
        {level}
      </button>
    {/each}
  </div>

  <!-- Tab Content -->
  <div class="mt-6">
    {#if retryingLevel === activeTab}
      <div class="rounded-xl border border-gray-200 bg-gray-50 p-12 text-center">
        <span class="material-symbols-outlined animate-spin text-indigo-400" style="font-size: 48px;">progress_activity</span>
        <p class="mt-3 text-sm text-gray-500">Retrying generation...</p>
      </div>
    {:else if activeError}
      <div class="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
        <span class="material-symbols-outlined text-red-400" style="font-size: 48px;">error</span>
        <p class="mt-2 text-sm text-red-600">{activeError}</p>
        <button
          onclick={() => retryLevel(activeTab)}
          class="mt-4 inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-red-700"
        >
          <span class="material-symbols-outlined" style="font-size: 16px;">refresh</span>
          Retry {activeTab}
        </button>
      </div>
    {:else if activeResult}
      {@const sample = activeResult.sample}
      {@const meta = activeResult.metadata}

      <div class="rounded-xl border border-gray-200 bg-white shadow-sm">
        <!-- Header -->
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 px-6 py-4">
          <div class="flex items-center gap-3">
            <span class="rounded-full {LEVEL_BG_CLASSES[activeTab]} px-3 py-1 text-xs font-semibold text-white">{activeTab}</span>
            <span class="text-sm text-gray-400">Grade {sample.persona_notes.grade_level}</span>
          </div>
          <div class="flex items-center gap-3 text-xs text-gray-400">
            <span>{sample.writing_traits.word_count} words</span>
            <span>{sample.writing_traits.paragraph_count} paragraphs</span>
            <span class="rounded bg-gray-100 px-2 py-0.5 capitalize">{sample.writing_traits.tone}</span>
          </div>
        </div>

        <!-- Body -->
        <div class="px-6 py-6 text-sm leading-relaxed text-gray-700">
          {#each sample.student_response.split('\n') as paragraph}
            {#if paragraph.trim()}
              <p class="mt-3 first:mt-0">{paragraph}</p>
            {/if}
          {/each}
        </div>

        <!-- Collapsible Details -->
        <details class="border-t border-gray-100">
          <summary class="cursor-pointer px-6 py-3 text-sm font-medium text-gray-500 hover:text-gray-700">
            View rubric scores, persona notes & metadata
          </summary>
          <div class="space-y-5 px-6 pb-6">
            <!-- Rubric Scores -->
            <div>
              <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400">Rubric Dimension Scores</h4>
              <div class="mt-2 flex flex-wrap gap-2">
                {#each Object.entries(sample.proficiency_scores) as [dim, score]}
                  {@const scoreColors: Record<string, string> = {
                    Exemplary: 'bg-blue-100 text-blue-700',
                    Proficient: 'bg-green-100 text-green-700',
                    Approaching: 'bg-amber-100 text-amber-700',
                    Below: 'bg-red-100 text-red-700'
                  }}
                  <span class="rounded-lg px-3 py-1.5 text-xs font-medium {scoreColors[score] ?? 'bg-gray-100 text-gray-600'}">
                    {dim}: {score}
                  </span>
                {/each}
              </div>
            </div>

            <!-- Persona Notes -->
            <div>
              <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400">Persona Notes</h4>
              <div class="mt-2 grid gap-3 sm:grid-cols-2">
                <div>
                  <p class="text-xs font-medium text-gray-500">Strengths</p>
                  <ul class="mt-1 list-inside list-disc text-xs text-gray-600">
                    {#each sample.persona_notes.writing_strengths as s}
                      <li>{s}</li>
                    {/each}
                  </ul>
                </div>
                <div>
                  <p class="text-xs font-medium text-gray-500">Weaknesses</p>
                  <ul class="mt-1 list-inside list-disc text-xs text-gray-600">
                    {#each sample.persona_notes.writing_weaknesses as w}
                      <li>{w}</li>
                    {/each}
                  </ul>
                </div>
              </div>
              {#if sample.persona_notes.error_patterns_applied.length > 0}
                <div class="mt-2">
                  <p class="text-xs font-medium text-gray-500">Error Patterns Applied</p>
                  <div class="mt-1 flex flex-wrap gap-1">
                    {#each sample.persona_notes.error_patterns_applied as ep}
                      <span class="rounded bg-orange-100 px-2 py-0.5 text-xs text-orange-700">{ep}</span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>

            <!-- Writing Traits -->
            <div>
              <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400">Writing Traits</h4>
              <div class="mt-2 flex flex-wrap gap-3 text-xs text-gray-600">
                <span>Avg sentence length: {sample.writing_traits.average_sentence_length} words</span>
              </div>
            </div>

            <!-- Token Usage -->
            {#if meta.token_usage}
              <div>
                <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400">Token Usage & Cost</h4>
                <div class="mt-2 grid gap-2 sm:grid-cols-2">
                  <div class="flex flex-wrap gap-3 text-xs text-gray-600">
                    <span>Input: {meta.token_usage.prompt_tokens.toLocaleString()}</span>
                    <span>Output: {meta.token_usage.completion_tokens.toLocaleString()}</span>
                    {#if meta.token_usage.thinking_tokens > 0}
                      <span>Thinking: {meta.token_usage.thinking_tokens.toLocaleString()}</span>
                    {/if}
                    <span class="font-medium">Total: {meta.token_usage.total_tokens.toLocaleString()}</span>
                  </div>
                  <div class="text-xs">
                    <span class="rounded bg-emerald-100 px-2 py-0.5 font-medium text-emerald-700">
                      Est. cost: ${meta.token_usage.estimated_cost_usd < 0.01 ? meta.token_usage.estimated_cost_usd.toFixed(4) : meta.token_usage.estimated_cost_usd.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            {/if}

            <!-- Metadata -->
            <div>
              <h4 class="text-xs font-semibold uppercase tracking-wide text-gray-400">Generation Metadata</h4>
              <div class="mt-2 flex flex-wrap gap-3 text-xs text-gray-400">
                <span>Model: {meta.model}</span>
                <span>Time: {meta.generation_time_ms}ms</span>
                {#if meta.template_used}
                  <span>Template: {meta.template_used}</span>
                {/if}
                <span>Request: {meta.request_id}</span>
              </div>
            </div>
          </div>
        </details>
      </div>
    {:else}
      <div class="rounded-xl border border-gray-200 bg-gray-50 p-12 text-center text-gray-400">
        No result for this level.
      </div>
    {/if}
  </div>

  <!-- Action Buttons -->
  <div class="mt-8 flex flex-wrap items-center gap-3">
    <button
      onclick={copyCurrent}
      disabled={!activeResult}
      class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
    >
      <span class="material-symbols-outlined" style="font-size: 16px;">content_copy</span>
      Copy
    </button>
    <button
      onclick={copyAll}
      class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50"
    >
      <span class="material-symbols-outlined" style="font-size: 16px;">copy_all</span>
      Copy All
    </button>
    <div class="flex-1"></div>
    <button
      onclick={editAndRegenerate}
      class="inline-flex items-center gap-2 rounded-lg border border-indigo-300 bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-700 shadow-sm transition hover:bg-indigo-100"
    >
      <span class="material-symbols-outlined" style="font-size: 16px;">edit</span>
      Edit & Regenerate
    </button>
    <button
      onclick={startOver}
      class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50"
    >
      <span class="material-symbols-outlined" style="font-size: 16px;">restart_alt</span>
      Start Over
    </button>
  </div>
</div>
