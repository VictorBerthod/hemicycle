<script lang="ts">
	interface Props {
		pour: number;
		contre: number;
		abst: number;
		height?: number;
	}

	let { pour, contre, abst, height = 8 }: Props = $props();

	let total = $derived(pour + contre + abst);
	let pPour   = $derived(total > 0 ? (pour   / total) * 100 : 0);
	let pContre = $derived(total > 0 ? (contre / total) * 100 : 0);
	let pAbst   = $derived(total > 0 ? (abst   / total) * 100 : 0);
</script>

<div class="vote-bar" style:height="{height}px" aria-label="Pour {pour}, Contre {contre}, Abstention {abst}">
	{#if total > 0}
		<div class="seg pour"   style:width="{pPour}%"></div>
		<div class="seg contre" style:width="{pContre}%"></div>
		<div class="seg abst"   style:width="{pAbst}%"></div>
	{/if}
</div>

<style>
	.vote-bar {
		display: flex;
		background: var(--rule);
		overflow: hidden;
	}

	.seg { height: 100%; }
	.seg.pour   { background: var(--pour); }
	.seg.contre { background: var(--contre); }
	.seg.abst   { background: var(--abst); }
</style>
