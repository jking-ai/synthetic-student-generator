<script lang="ts">
  import { currentScreen } from '$lib/stores';

  const steps = [
    { icon: 'menu_book', title: 'Choose a Rubric', description: 'Pick from a built-in template or paste your own rubric from any source.' },
    { icon: 'edit_note', title: 'Enter Your Prompt', description: 'Type the writing prompt exactly as you would give it to your students.' },
    { icon: 'groups', title: 'Get Student Samples', description: 'Receive realistic writing samples at each proficiency level, ready for calibration.' }
  ];
</script>

<div class="mx-auto max-w-6xl px-6 py-12">
  <!-- Hero -->
  <div class="text-center">
    <h2 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
      Synthetic Student Generator
    </h2>
    <p class="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
      Generate realistic student writing samples for grading calibration &mdash; in seconds, not hours.
    </p>
  </div>

  <!-- Steps -->
  <div class="mt-16 grid gap-8 sm:grid-cols-3">
    {#each steps as step, i}
      <div class="rounded-xl border border-gray-200 bg-white p-6 text-center shadow-sm transition hover:shadow-md">
        <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100">
          <span class="material-symbols-outlined text-indigo-600" style="font-size: 28px;">{step.icon}</span>
        </div>
        <div class="mt-2 text-xs font-semibold uppercase tracking-wide text-indigo-500">Step {i + 1}</div>
        <h3 class="mt-2 text-lg font-semibold text-gray-900">{step.title}</h3>
        <p class="mt-2 text-sm text-gray-500">{step.description}</p>
      </div>
    {/each}
  </div>

  <!-- Example Output -->
  <div class="mt-16">
    <h3 class="text-center text-sm font-semibold uppercase tracking-wide text-gray-400">Example Output</h3>
    <div class="mx-auto mt-4 max-w-2xl rounded-xl border border-gray-200 bg-white shadow-sm">
      <div class="flex items-center justify-between border-b border-gray-100 px-6 py-4">
        <div class="flex items-center gap-3">
          <span class="rounded-full bg-green-500 px-3 py-1 text-xs font-semibold text-white">Proficient</span>
          <span class="text-sm text-gray-400">Grade 8 &middot; Argumentative Essay</span>
        </div>
        <div class="flex items-center gap-3 text-xs text-gray-400">
          <span>247 words</span>
          <span class="rounded bg-gray-100 px-2 py-0.5">Earnest</span>
        </div>
      </div>
      <div class="px-6 py-5 text-sm leading-relaxed text-gray-700">
        <p>
          I think that school uniforms are a good idea because they help students focus on learning instead of worrying about what to wear. When everyone is dressed the same, there is less bullying about clothes and students can concentrate on their work.
        </p>
        <p class="mt-3">
          Some people say that uniforms take away freedom of expression, but I disagree. Students can still express themselves through their work, their ideas, and their actions. Uniforms actually make things more fair because not everyone can afford expensive clothes.
        </p>
        <p class="mt-3">
          In conclusion, school uniforms create a better learning environment for all students. They reduce distractions and help everyone feel like they belong.
        </p>
      </div>
      <div class="flex items-center gap-2 border-t border-gray-100 px-6 py-3 text-xs text-gray-400">
        <span class="material-symbols-outlined" style="font-size: 14px;">info</span>
        <span>Includes persona notes, rubric scores, and writing trait metadata</span>
      </div>
    </div>
  </div>

  <!-- CTA -->
  <div class="mt-12 text-center">
    <button
      onclick={() => currentScreen.set('configure')}
      class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-8 py-3.5 text-base font-semibold text-white shadow-md transition hover:bg-indigo-700 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
    >
      <span class="material-symbols-outlined" style="font-size: 20px;">add_circle</span>
      Create Calibration Set
    </button>
  </div>
</div>
