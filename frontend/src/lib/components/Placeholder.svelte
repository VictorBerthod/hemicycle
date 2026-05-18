<script lang="ts">
	interface Props {
		width?: string;
		height?: string;
		inline?: boolean;
	}

	let { width = '100%', height = '1em', inline = false }: Props = $props();
</script>

<span
	class="placeholder"
	class:inline
	style:width
	style:height
	aria-hidden="true"
></span>

<style>
	.placeholder {
		display: block;
		background: var(--bg-alt);
		animation: pulse 1.4s ease-in-out infinite;
	}

	.placeholder.inline {
		display: inline-block;
		vertical-align: middle;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50%       { opacity: 0.4; }
	}

	@media (prefers-reduced-motion: reduce) {
		.placeholder { animation: none; }
	}
</style>
