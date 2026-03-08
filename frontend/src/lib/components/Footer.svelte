<script lang="ts">
  import { onMount } from 'svelte';
  import { checkHealth } from '$lib/api';

  const quotes = [
    { text: 'The art of teaching is the art of assisting discovery.', author: 'Mark Van Doren' },
    { text: 'Every student can learn, just not on the same day, or the same way.', author: 'George Evans' },
    { text: 'Teaching is the greatest act of optimism.', author: 'Colleen Wilcox' },
    { text: 'Education is not the filling of a pail, but the lighting of a fire.', author: 'W.B. Yeats' },
    { text: 'The best teachers teach from the heart, not from the book.', author: 'Unknown' },
    { text: 'What we learn with pleasure we never forget.', author: 'Alfred Mercier' },
    { text: 'A good teacher can inspire hope, ignite the imagination, and instill a love of learning.', author: 'Brad Henry' }
  ];

  let quote = $state(quotes[0]);
  let apiStatus = $state<'checking' | 'warming' | 'online' | 'offline'>('checking');

  async function pollHealth() {
    apiStatus = 'checking';
    let warmingTimeout: ReturnType<typeof setTimeout> | undefined;

    try {
      warmingTimeout = setTimeout(() => {
        if (apiStatus === 'checking') {
          apiStatus = 'warming';
        }
      }, 2000);

      await checkHealth();
      apiStatus = 'online';
    } catch {
      apiStatus = 'offline';
    } finally {
      if (warmingTimeout) clearTimeout(warmingTimeout);
    }
  }

  onMount(() => {
    quote = quotes[Math.floor(Math.random() * quotes.length)];
    pollHealth();
    const interval = setInterval(pollHealth, 60000);
    return () => clearInterval(interval);
  });

  const statusConfig = $derived({
    checking: { color: 'bg-gray-400', label: 'Checking API...', pulse: true },
    warming: { color: 'bg-amber-400', label: 'API warming up...', pulse: true },
    online: { color: 'bg-green-500', label: 'API online', pulse: false },
    offline: { color: 'bg-red-500', label: 'API offline', pulse: false }
  }[apiStatus]);
</script>

<footer class="border-t border-gray-200 bg-white px-6 py-3">
  <div class="mx-auto flex max-w-6xl items-center justify-between text-sm text-gray-500">
    <div class="flex items-center gap-2">
      <span class="material-symbols-outlined text-indigo-400" style="font-size: 18px;">school</span>
      <span class="italic">"{quote.text}"</span>
      <span class="hidden sm:inline">&mdash; {quote.author}</span>
    </div>
    <div class="flex items-center gap-2">
      <span class="relative flex h-2.5 w-2.5">
        {#if statusConfig.pulse}
          <span class="absolute inline-flex h-full w-full animate-ping rounded-full {statusConfig.color} opacity-75"></span>
        {/if}
        <span class="relative inline-flex h-2.5 w-2.5 rounded-full {statusConfig.color}"></span>
      </span>
      <span>{statusConfig.label}</span>
    </div>
  </div>
</footer>
