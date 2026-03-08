<script lang="ts">
  import '../app.css';
  import Footer from '$lib/components/Footer.svelte';

  let { children } = $props();
</script>

<div class="flex min-h-screen flex-col bg-gray-50">
  <header class="border-b border-gray-200 bg-white shadow-sm">
    <div class="mx-auto flex max-w-6xl items-center gap-3 px-6 py-4">
      <span class="material-symbols-outlined text-indigo-600" style="font-size: 28px;">psychology</span>
      <h1 class="text-lg font-semibold text-gray-900">Synthetic Student Generator</h1>
    </div>
  </header>

  <main class="flex-1">
    {@render children()}
  </main>

  <Footer />
</div>
