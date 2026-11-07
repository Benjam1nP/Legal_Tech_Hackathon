<script lang="ts">
	import { mode, toggleMode } from 'mode-watcher';
	import Moon from '~icons/ph/moon';
	import Sun from '~icons/ph/sun';
	import { Button } from '$lib/components/ui/button';

	const dark = $derived(mode.current === 'dark');
</script>

<Button
	variant="ghost"
	size="icon-sm"
	class="size-11 md:size-8"
	onclick={toggleMode}
	aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
>
	{#if dark}<Sun class="size-5" />{:else}<Moon class="size-5" />{/if}
</Button>
