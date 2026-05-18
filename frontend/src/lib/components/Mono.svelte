<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children?: Snippet;
		color?: string;
		size?: number;
	}

	let { children, color, size }: Props = $props();
</script>

<span
	class="mono-atom"
	style:color={color}
	style:font-size={size ? `${size}px` : undefined}
>
	{#if children}{@render children()}{/if}
</span>

<style>
	.mono-atom {
		font-family: var(--font-mono);
		font-size: 12px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--muted);
	}
</style>
