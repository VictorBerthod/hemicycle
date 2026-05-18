<script lang="ts">
	import type { VotePosition } from '$lib/tokens';

	interface Props {
		position: VotePosition;
		size?: number;
	}

	let { position, size = 12 }: Props = $props();

	let absent = $derived(position === 'absent');
</script>

<span
	class="vote-dot"
	class:absent
	style:width="{size}px"
	style:height="{size}px"
	style:--pos-color="var(--{position})"
	aria-label={position}
	role="img"
></span>

<style>
	.vote-dot {
		display: inline-block;
		flex-shrink: 0;
		border-radius: 50%;
		background: var(--pos-color);
		border: none;
		vertical-align: middle;
	}

	.vote-dot.absent {
		background: transparent;
		border: 1px dashed var(--muted);
	}
</style>
