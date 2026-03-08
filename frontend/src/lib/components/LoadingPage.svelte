<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import {
    currentScreen,
    selectedTemplateId,
    rubricMode,
    customRubricText,
    assignmentPrompt,
    gradeLevel,
    selectedLevels,
    results,
    errors
  } from '$lib/stores';
  import { generate } from '$lib/api';
  import { LEVEL_BG_CLASSES, LEVEL_TEXT_CLASSES, type ProficiencyLevel } from '$lib/types';

  let levels = $state<ProficiencyLevel[]>([]);
  let completedLevels = $state<ProficiencyLevel[]>([]);
  let failedLevels = $state<ProficiencyLevel[]>([]);
  let retryingLevels = $state<ProficiencyLevel[]>([]);
  let errorMessages = $state<Record<string, string>>({});

  const totalDone = $derived(completedLevels.length + failedLevels.length);
  const allDone = $derived(totalDone === levels.length && levels.length > 0);

  function isCompleted(level: ProficiencyLevel): boolean {
    return completedLevels.includes(level);
  }

  function isFailed(level: ProficiencyLevel): boolean {
    return failedLevels.includes(level);
  }

  function isRetrying(level: ProficiencyLevel): boolean {
    return retryingLevels.includes(level);
  }

  onMount(() => {
    const levelsArr = [...get(selectedLevels)];
    levels = levelsArr;

    const prompt = get(assignmentPrompt);
    const grade = get(gradeLevel);
    const mode = get(rubricMode);
    const templateId = get(selectedTemplateId);
    const rubricText = get(customRubricText);

    for (const level of levelsArr) {
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

      generate(params as any)
        .then((res) => {
          results.update((current) => ({ ...current, [level]: res }));
          completedLevels = [...completedLevels, level];
        })
        .catch(() => {
          // Auto-retry once
          retryingLevels = [...retryingLevels, level];
          generate(params as any)
            .then((res) => {
              retryingLevels = retryingLevels.filter(l => l !== level);
              results.update((current) => ({ ...current, [level]: res }));
              completedLevels = [...completedLevels, level];
            })
            .catch((err2) => {
              retryingLevels = retryingLevels.filter(l => l !== level);
              const msg = err2 instanceof Error ? err2.message : 'Generation failed';
              errors.update((current) => ({ ...current, [level]: msg }));
              errorMessages = { ...errorMessages, [level]: msg };
              failedLevels = [...failedLevels, level];
            });
        });
    }
  });

  $effect(() => {
    if (allDone) {
      const timer = setTimeout(() => {
        currentScreen.set('results');
      }, 1000);
      return () => clearTimeout(timer);
    }
  });
</script>

<div class="mx-auto max-w-xl px-6 py-16">
  <div class="text-center">
    <h2 class="text-2xl font-bold text-gray-900">Generating Samples</h2>
    <p class="mt-2 text-sm text-gray-500">
      Creating student writing for each proficiency level... ({totalDone}/{levels.length})
    </p>
  </div>

  <div class="mt-10 space-y-4">
    {#each levels as level}
      <div class="flex items-center gap-4 rounded-xl border border-gray-200 bg-white px-5 py-4 shadow-sm">
        <span class="h-4 w-4 rounded-full {LEVEL_BG_CLASSES[level]}"></span>
        <span class="flex-1 font-medium {LEVEL_TEXT_CLASSES[level]}">{level}</span>

        {#if isCompleted(level)}
          <span class="material-symbols-outlined text-green-500" style="font-size: 24px;">check_circle</span>
        {:else if isFailed(level)}
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-red-500" style="font-size: 24px;">cancel</span>
            <span class="text-xs text-red-500">{errorMessages[level]}</span>
          </div>
        {:else if isRetrying(level)}
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined animate-spin text-amber-500" style="font-size: 24px;">progress_activity</span>
            <span class="text-xs text-amber-500">Retrying...</span>
          </div>
        {:else}
          <span class="material-symbols-outlined animate-spin text-indigo-400" style="font-size: 24px;">progress_activity</span>
        {/if}
      </div>
    {/each}
  </div>

  {#if allDone}
    <div class="mt-8 text-center">
      <button
        onclick={() => currentScreen.set('results')}
        class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-indigo-700"
      >
        <span class="material-symbols-outlined" style="font-size: 18px;">visibility</span>
        View Results
      </button>
    </div>
  {/if}
</div>
