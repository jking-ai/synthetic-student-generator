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
    templates,
    results,
    errors
  } from '$lib/stores';
  import { getTemplates } from '$lib/api';
  import { PROFICIENCY_LEVELS, LEVEL_BG_CLASSES, type ProficiencyLevel } from '$lib/types';

  let localTemplates = $state(get(templates));
  let localRubricMode = $state(get(rubricMode));
  let localSelectedTemplateId = $state(get(selectedTemplateId));
  let localCustomRubricText = $state(get(customRubricText));
  let localAssignmentPrompt = $state(get(assignmentPrompt));
  let localGradeLevel = $state(get(gradeLevel));
  let localSelectedLevels = $state<ProficiencyLevel[]>([...get(selectedLevels)]);
  let expandedTemplateId = $state<string | null>(null);
  let loadingTemplates = $state(true);
  let templateError = $state<string | null>(null);

  const gradeOptions = Array.from({ length: 10 }, (_, i) => i + 3);

  const canGenerate = $derived(
    localAssignmentPrompt.trim().length > 0 &&
    localSelectedLevels.length > 0 &&
    (localRubricMode === 'custom' ? localCustomRubricText.trim().length > 0 : localSelectedTemplateId !== null)
  );

  const sampleCount = $derived(localSelectedLevels.length);

  function isLevelSelected(level: ProficiencyLevel): boolean {
    return localSelectedLevels.includes(level);
  }

  onMount(async () => {
    try {
      const data = await getTemplates();
      localTemplates = data.templates ?? data;
      templates.set(localTemplates);
    } catch {
      templateError = 'Could not load rubric templates. You can still paste your own rubric.';
    } finally {
      loadingTemplates = false;
    }
  });

  function toggleLevel(level: ProficiencyLevel) {
    const idx = localSelectedLevels.indexOf(level);
    if (idx >= 0) {
      // Don't remove the last one
      if (localSelectedLevels.length > 1) {
        localSelectedLevels = localSelectedLevels.filter(l => l !== level);
      }
    } else {
      localSelectedLevels = [...localSelectedLevels, level];
    }
  }

  function handleGenerate() {
    // Sync stores
    rubricMode.set(localRubricMode);
    selectedTemplateId.set(localSelectedTemplateId);
    customRubricText.set(localCustomRubricText);
    assignmentPrompt.set(localAssignmentPrompt);
    gradeLevel.set(localGradeLevel);
    selectedLevels.set([...localSelectedLevels]);
    results.set({});
    errors.set({});

    currentScreen.set('loading');
  }
</script>

<div class="mx-auto max-w-3xl px-6 py-8">
  <!-- Back button -->
  <button
    onclick={() => currentScreen.set('landing')}
    class="mb-6 inline-flex items-center gap-1 text-sm text-gray-500 transition hover:text-gray-700"
  >
    <span class="material-symbols-outlined" style="font-size: 18px;">arrow_back</span>
    Back
  </button>

  <h2 class="text-2xl font-bold text-gray-900">Configure Your Calibration Set</h2>
  <p class="mt-1 text-sm text-gray-500">Set up your rubric, assignment prompt, and proficiency levels.</p>

  <!-- Section A: Rubric Selection -->
  <section class="mt-8">
    <h3 class="flex items-center gap-2 text-lg font-semibold text-gray-900">
      <span class="material-symbols-outlined text-indigo-500" style="font-size: 22px;">menu_book</span>
      Rubric
    </h3>

    <!-- Toggle -->
    <div class="mt-4 flex gap-2">
      <button
        onclick={() => { localRubricMode = 'template'; }}
        class="rounded-lg px-4 py-2 text-sm font-medium transition {localRubricMode === 'template' ? 'bg-indigo-600 text-white shadow-sm' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}"
      >
        Use a Template
      </button>
      <button
        onclick={() => { localRubricMode = 'custom'; }}
        class="rounded-lg px-4 py-2 text-sm font-medium transition {localRubricMode === 'custom' ? 'bg-indigo-600 text-white shadow-sm' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}"
      >
        Paste Your Own
      </button>
    </div>

    {#if localRubricMode === 'template'}
      <div class="mt-4">
        {#if loadingTemplates}
          <div class="flex items-center gap-2 text-sm text-gray-400">
            <span class="material-symbols-outlined animate-spin" style="font-size: 18px;">progress_activity</span>
            Loading templates...
          </div>
        {:else if templateError}
          <div class="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
            {templateError}
          </div>
        {:else}
          <div class="grid gap-3 sm:grid-cols-2">
            {#each localTemplates as template}
              <button
                onclick={() => {
                  localSelectedTemplateId = template.id;
                  expandedTemplateId = expandedTemplateId === template.id ? null : template.id;
                }}
                class="rounded-xl border-2 p-4 text-left transition hover:shadow-md {localSelectedTemplateId === template.id ? 'border-indigo-500 bg-indigo-50 shadow-sm' : 'border-gray-200 bg-white'}"
              >
                <h4 class="font-semibold text-gray-900">{template.name}</h4>
                <p class="mt-1 text-xs text-gray-500">{template.description}</p>
                <div class="mt-2 flex items-center gap-3 text-xs text-gray-400">
                  <span>Grades {template.grade_range}</span>
                  <span>{template.dimensions.length} dimensions</span>
                </div>
                {#if expandedTemplateId === template.id && localSelectedTemplateId === template.id}
                  <div class="mt-3 border-t border-gray-100 pt-3">
                    <p class="text-xs font-medium text-gray-500">Dimensions:</p>
                    <div class="mt-1 flex flex-wrap gap-1">
                      {#each template.dimensions as dim}
                        <span class="rounded bg-indigo-100 px-2 py-0.5 text-xs text-indigo-700">
                          {typeof dim === 'string' ? dim : dim.name}
                        </span>
                      {/each}
                    </div>
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        {/if}
      </div>
    {:else}
      <div class="mt-4">
        <textarea
          bind:value={localCustomRubricText}
          placeholder="Paste your rubric here — from your LMS, a document, or type it out..."
          rows="8"
          class="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-sm text-gray-700 shadow-sm transition placeholder:text-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
        ></textarea>
      </div>
    {/if}
  </section>

  <!-- Section B: Assignment Details -->
  <section class="mt-10">
    <h3 class="flex items-center gap-2 text-lg font-semibold text-gray-900">
      <span class="material-symbols-outlined text-indigo-500" style="font-size: 22px;">edit_note</span>
      Assignment Details
    </h3>

    <div class="mt-4 space-y-4">
      <div>
        <label for="prompt" class="block text-sm font-medium text-gray-700">Assignment Prompt</label>
        <textarea
          id="prompt"
          bind:value={localAssignmentPrompt}
          placeholder="Enter the writing prompt you'd give to students..."
          rows="4"
          class="mt-1 w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-sm text-gray-700 shadow-sm transition placeholder:text-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
        ></textarea>
      </div>

      <div>
        <label for="grade" class="block text-sm font-medium text-gray-700">Grade Level</label>
        <select
          id="grade"
          bind:value={localGradeLevel}
          class="mt-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
        >
          {#each gradeOptions as g}
            <option value={g}>Grade {g}</option>
          {/each}
        </select>
      </div>

      <div>
        <span class="block text-sm font-medium text-gray-700">Proficiency Levels</span>
        <p class="text-xs text-gray-400">Select which levels to generate (at least 1 required).</p>
        <div class="mt-2 flex flex-wrap gap-3">
          {#each PROFICIENCY_LEVELS as level}
            {@const selected = isLevelSelected(level)}
            <button
              onclick={() => toggleLevel(level)}
              class="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition {selected ? 'border-gray-300 bg-white shadow-sm' : 'border-gray-200 bg-gray-50 text-gray-400'}"
            >
              <span class="h-3 w-3 rounded-full {LEVEL_BG_CLASSES[level]} {selected ? 'opacity-100' : 'opacity-30'}"></span>
              {level}
              {#if selected}
                <span class="material-symbols-outlined text-green-500" style="font-size: 16px;">check_circle</span>
              {/if}
            </button>
          {/each}
        </div>
      </div>
    </div>
  </section>

  <!-- Section C: Generate -->
  <section class="mt-10 pb-8">
    <button
      onclick={handleGenerate}
      disabled={!canGenerate}
      class="inline-flex w-full items-center justify-center gap-2 rounded-xl py-3.5 text-base font-semibold shadow-md transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 {canGenerate ? 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-lg' : 'cursor-not-allowed bg-gray-200 text-gray-400'}"
    >
      <span class="material-symbols-outlined" style="font-size: 20px;">auto_awesome</span>
      Generate {sampleCount} Sample{sampleCount !== 1 ? 's' : ''}
    </button>
  </section>
</div>
