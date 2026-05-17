<script lang="ts">
	import { onMount } from 'svelte';

	interface GroupComposition {
		acronyme: string;
		nom: string;
		count: number;
	}

	let { data }: { data: GroupComposition[] } = $props();

	// Official political colors (left to right spectrum)
	const GROUP_COLORS: Record<string, string> = {
		'LFI-NFP': '#cc2443',
		'GDR': '#c2001e',
		'ECOS': '#00c000',
		'SOC': '#ff8080',
		'LIOT': '#22aabb',
		'DEM': '#ff9900',
		'EPR': '#ffcc00',
		'HOR': '#00bbff',
		'DR': '#0066cc',
		'UDDPLR': '#0044aa',
		'RN': '#0d378a',
		'NI': '#888888',
	};

	// Political spectrum order (left to right)
	const SPECTRUM_ORDER = [
		'LFI-NFP', 'GDR', 'ECOS', 'SOC', 'LIOT',
		'DEM', 'EPR', 'HOR', 'DR', 'UDDPLR', 'RN', 'NI'
	];

	interface Seat {
		x: number;
		y: number;
		color: string;
		groupe: string;
	}

	let seats = $derived.by(() => {
		if (!data || data.length === 0) return [];

		// Sort groups by political spectrum
		const sorted = [...data].sort((a, b) => {
			const ia = SPECTRUM_ORDER.indexOf(a.acronyme);
			const ib = SPECTRUM_ORDER.indexOf(b.acronyme);
			return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
		});

		const totalSeats = sorted.reduce((s, g) => s + g.count, 0);
		const result: Seat[] = [];

		// Hemicycle geometry: semicircle with multiple rows
		const rows = 10;
		const centerX = 300;
		const centerY = 280;
		const minRadius = 80;
		const maxRadius = 250;

		// Distribute seats across rows (more seats in outer rows)
		const seatsPerRow: number[] = [];
		let totalCapacity = 0;
		for (let r = 0; r < rows; r++) {
			const radius = minRadius + (maxRadius - minRadius) * (r / (rows - 1));
			const capacity = Math.floor(Math.PI * radius / 12);
			seatsPerRow.push(capacity);
			totalCapacity += capacity;
		}

		// Scale to fit actual total
		const scale = totalSeats / totalCapacity;
		const actualSeatsPerRow = seatsPerRow.map((c, i) => {
			if (i === rows - 1) {
				// Last row gets remainder
				return totalSeats - result.length;
			}
			return Math.round(c * scale);
		});

		// Flatten groups into seat array ordered by spectrum
		const allSeats: { color: string; groupe: string }[] = [];
		for (const g of sorted) {
			for (let i = 0; i < g.count; i++) {
				allSeats.push({ color: GROUP_COLORS[g.acronyme] || '#666', groupe: g.acronyme });
			}
		}

		let seatIdx = 0;
		for (let r = 0; r < rows; r++) {
			const radius = minRadius + (maxRadius - minRadius) * (r / (rows - 1));
			const count = Math.min(actualSeatsPerRow[r], totalSeats - seatIdx);
			if (count <= 0) break;

			for (let i = 0; i < count; i++) {
				if (seatIdx >= allSeats.length) break;
				// Angle from left (PI) to right (0)
				const angle = Math.PI - (Math.PI * (i + 0.5)) / count;
				const x = centerX + radius * Math.cos(angle);
				const y = centerY - radius * Math.sin(angle);
				result.push({
					x,
					y,
					color: allSeats[seatIdx].color,
					groupe: allSeats[seatIdx].groupe,
				});
				seatIdx++;
			}
		}

		return result;
	});

	let hoveredGroup = $state<string | null>(null);
</script>

<div class="hemicycle-container">
	<svg viewBox="0 0 600 300" role="img" aria-label="Hemicycle de l'Assemblee nationale">
		{#each seats as seat}
			<circle
				cx={seat.x}
				cy={seat.y}
				r="4.5"
				fill={seat.color}
				opacity={hoveredGroup === null || hoveredGroup === seat.groupe ? 1 : 0.15}
				onmouseenter={() => hoveredGroup = seat.groupe}
				onmouseleave={() => hoveredGroup = null}
			/>
		{/each}
	</svg>

	{#if data && data.length > 0}
		<div class="legend">
			{#each [...data].sort((a, b) => {
				const ia = SPECTRUM_ORDER.indexOf(a.acronyme);
				const ib = SPECTRUM_ORDER.indexOf(b.acronyme);
				return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
			}) as g}
				<button
					class="legend-item"
					class:dimmed={hoveredGroup !== null && hoveredGroup !== g.acronyme}
					onmouseenter={() => hoveredGroup = g.acronyme}
					onmouseleave={() => hoveredGroup = null}
				>
					<span class="legend-dot" style="background: {GROUP_COLORS[g.acronyme] || '#666'}"></span>
					<span class="legend-label">{g.acronyme}</span>
					<span class="legend-count">{g.count}</span>
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	.hemicycle-container {
		width: 100%;
		max-width: 600px;
		margin: 0 auto;
	}

	svg {
		width: 100%;
		height: auto;
	}

	circle {
		transition: opacity 0.2s;
	}

	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.4rem;
		margin-top: 0.75rem;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.75rem;
		background: none;
		border: none;
		color: var(--text);
		cursor: pointer;
		padding: 0.2rem 0.4rem;
		border-radius: 3px;
		transition: opacity 0.2s;
	}

	.legend-item:hover {
		background: var(--bg-hover);
	}

	.legend-item.dimmed {
		opacity: 0.3;
	}

	.legend-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.legend-label {
		font-weight: 600;
	}

	.legend-count {
		color: var(--text-muted);
	}
</style>
