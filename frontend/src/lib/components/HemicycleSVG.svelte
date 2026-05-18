<script lang="ts">
	import { GROUP_COLORS, SPECTRUM } from '$lib/tokens';

	interface GroupEntry {
		acronym: string;
		count: number;
	}

	interface Seat {
		x: number;
		y: number;
		color: string;
		acronym: string;
	}

	interface Props {
		composition: GroupEntry[];
		votes?: string[];
		width?: number;
		height?: number;
		dotR?: number;
	}

	let { composition, votes, width = 600, height = 320, dotR = 4.5 }: Props = $props();

	const VOTE_COLORS: Record<string, string> = {
		pour:    'var(--pour)',
		contre:  'var(--contre)',
		abst:    'var(--abst)',
		absent:  'var(--absent)',
	};

	const ROWS = 10;

	let seats = $derived.by<Seat[]>(() => {
		if (!composition || composition.length === 0) return [];

		const centerX = width / 2;
		const centerY = height - 30;
		const minR = 70;
		const maxR = Math.min(width, height * 2) / 2 - 20;

		const totalSeats = composition.reduce((s, g) => s + g.count, 0);

		// Row capacities (proportional to arc length)
		const caps: number[] = [];
		let totalCap = 0;
		for (let r = 0; r < ROWS; r++) {
			const rad = minR + (maxR - minR) * (r / (ROWS - 1));
			const c = Math.floor(Math.PI * rad / 12);
			caps.push(c);
			totalCap += c;
		}
		const scale = totalSeats / totalCap;
		const actual = caps.map((c, i) => (i === ROWS - 1 ? null : Math.round(c * scale)));

		// Sort by spectrum and flatten to seat array
		const spectrum = SPECTRUM as readonly string[];
		const sorted = [...composition].sort((a, b) => {
			const ia = spectrum.indexOf(a.acronym);
			const ib = spectrum.indexOf(b.acronym);
			return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
		});

		const flat: { acronym: string; color: string }[] = [];
		for (const g of sorted) {
			const color = GROUP_COLORS[g.acronym] ?? '#888888';
			for (let i = 0; i < g.count; i++) flat.push({ acronym: g.acronym, color });
		}

		const result: Seat[] = [];
		let idx = 0;

		for (let r = 0; r < ROWS; r++) {
			const rad = minR + (maxR - minR) * (r / (ROWS - 1));
			const count = actual[r] ?? totalSeats - idx;
			const n = Math.min(count, flat.length - idx);
			if (n <= 0) break;

			for (let i = 0; i < n; i++) {
				const angle = Math.PI - (Math.PI * (i + 0.5)) / n;
				const x = centerX + rad * Math.cos(angle);
				const y = centerY - rad * Math.sin(angle);
				const entry = flat[idx];
				const color = votes
					? (VOTE_COLORS[votes[idx]] ?? VOTE_COLORS.absent)
					: entry.color;
				result.push({ x, y, color, acronym: entry.acronym });
				idx++;
			}
		}

		return result;
	});
</script>

<svg
	viewBox="0 0 {width} {height}"
	style:width="100%"
	style:height="auto"
	style:display="block"
	role="img"
	aria-label="Hémicycle de l'Assemblée nationale"
>
	{#each seats as seat (seat.x + ',' + seat.y)}
		<circle
			cx={seat.x}
			cy={seat.y}
			r={dotR}
			fill={seat.color}
			role="presentation"
		/>
	{/each}
</svg>
