<script lang="ts">
  import { currentScreen } from '$lib/stores';
  import LandingPage from '$lib/components/LandingPage.svelte';
  import ConfigurePage from '$lib/components/ConfigurePage.svelte';
  import LoadingPage from '$lib/components/LoadingPage.svelte';
  import ResultsPage from '$lib/components/ResultsPage.svelte';
</script>

{#if $currentScreen === 'landing'}
  <LandingPage />
{:else if $currentScreen === 'configure'}
  <ConfigurePage />
{:else if $currentScreen === 'loading'}
  <LoadingPage />
{:else if $currentScreen === 'results'}
  <ResultsPage />
{/if}
