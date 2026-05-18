<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getStats, getComposition, getScrutins, getEcarts, getThemes,
		type Stats, type GroupComposition, type ScrutinListItem, type EcartOut, type ThemeOut,
	} from '$lib/api';
	import { getGroupColor } from '$lib/tokens';
	import HemicycleSVG from '$lib/components/HemicycleSVG.svelte';
	import Eyebrow from '$lib/components/Eyebrow.svelte';
	import VoteBadge from '$lib/components/VoteBadge.svelte';
	import VoteBar from '$lib/components/VoteBar.svelte';
	import PartyTag from '$lib/components/PartyTag.svelte';
	import Mono from '$lib/components/Mono.svelte';

	let stats = $state<Stats | null>(null);
	let composition = $state<GroupComposition[]>([]);
	let scrutins = $state<ScrutinListItem[]>([]);
	let ecarts = $state<EcartOut[]>([]);
	let themes = $state<ThemeOut[]>([]);
	let error = $state('');

	onMount(async () => {
		try {
			const [s, c, sc, e, t] = await Promise.all([
				getStats(),
				getComposition(),
				getScrutins({ page: 1 }),
				getEcarts(4),
				getThemes(),
			]);
			stats = s;
			composition = c;
			scrutins = sc.slice(0, 5);
			ecarts = e;
			themes = t;
		} catch {
			error = 'Impossible de charger les données. Le backend est-il lancé ?';
		}
	});

	// Map composition to HemicycleSVG format (acronym instead of acronyme)
	let hemiCompo = $derived(composition.map(g => ({ acronym: g.acronyme, count: g.count })));

	function formatDate(d: string) {
		return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
	}
</script>

<svelte:head>
	<title>[PROJET].fr — Transparence parlementaire française</title>
</svelte:head>

<!-- ── HERO ──────────────────────────────────────────────────────────────── -->
<section class="hero">
	<Eyebrow>Note de la rédaction · {new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</Eyebrow>
	<h1>Ce qui se vote,<br/><em>et ce qui s'en dit</em>.</h1>
	<p class="hero-lede">
		Une base de données factuelle et sourcée de la vie parlementaire française, croisée avec
		la parole publique de celles et ceux qui font la loi.
	</p>
	{#if error}
		<p class="error-msg">{error}</p>
	{/if}
	<div class="hero-stats">
		<span><strong>{stats?.total_deputes ?? 577}</strong> députés suivis</span>
		<span class="sep">·</span>
		<span><strong>{stats?.total_scrutins?.toLocaleString('fr-FR') ?? '—'}</strong> scrutins publics</span>
		<span class="sep">·</span>
		<span><strong>{stats?.total_votes?.toLocaleString('fr-FR') ?? '—'}</strong> votes enregistrés</span>
		<span class="sep">·</span>
		<span class="accent"><strong>314</strong> écarts documentés</span>
	</div>
</section>

<!-- ── HÉMICYCLE ──────────────────────────────────────────────────────────── -->
{#if composition.length > 0}
<section class="hemicycle-section">
	<div class="hemicycle-grid">
		<div class="hemicycle-text">
			<Eyebrow>Hémicycle · état des forces</Eyebrow>
			<h2>
				577 sièges, douze formations,<br/>
				<em>une seule donnée</em>.
			</h2>
			<p>
				Composition actuelle de l'Assemblée nationale. Survolez un groupe pour
				mettre ses élus en relief, cliquez pour accéder à la liste.
			</p>
			<div class="group-legend">
				{#each composition as g (g.acronyme)}
					<a href="/personnalites?groupe={g.acronyme}" class="legend-row">
						<span class="dot" style:background={getGroupColor(g.acronyme)}></span>
						<span class="acro">{g.acronyme}</span>
						<span class="gnom">{g.nom}</span>
						<span class="gcnt">{g.count}</span>
					</a>
				{/each}
			</div>
		</div>
		<div class="hemicycle-svg">
			<HemicycleSVG composition={hemiCompo} />
			<Mono>Source : data.assemblee-nationale.fr</Mono>
		</div>
	</div>
</section>
{/if}

<!-- ── SCRUTINS ───────────────────────────────────────────────────────────── -->
{#if scrutins.length > 0}
<section class="scrutins-section">
	<div class="section-header">
		<h2>Scrutins récents</h2>
		<a href="/scrutins" class="see-all"><Mono color="var(--accent)">Tous les scrutins →</Mono></a>
	</div>
	<table class="scrutins-table">
		<thead>
			<tr>
				{#each ['n°', 'Titre', 'Date', 'Résultat', 'Répartition', 'Pour', 'Contre', 'Abst.'] as h (h)}
					<th>{h}</th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{#each scrutins as s (s.id)}
				<tr>
					<td class="num"><a href="/scrutin/{s.numero}">n°{s.numero}</a></td>
					<td class="titre">
						<a href="/scrutin/{s.numero}">{s.titre}</a>
					</td>
					<td class="date">{formatDate(s.date_scrutin)}</td>
					<td><VoteBadge position={s.sort === 'adopte' ? 'adopte' : 'rejete'} /></td>
					<td class="bar-cell"><VoteBar pour={s.nb_pour} contre={s.nb_contre} abst={s.nb_abstention} /></td>
					<td class="vote-num pour">{s.nb_pour}</td>
					<td class="vote-num contre">{s.nb_contre}</td>
					<td class="vote-num abst">{s.nb_abstention}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</section>
{/if}

<!-- ── ÉCARTS ─────────────────────────────────────────────────────────────── -->
{#if ecarts.length > 0}
<section class="ecarts-section">
	<div class="section-header">
		<div>
			<Eyebrow>Écarts documentés · 7 derniers jours</Eyebrow>
			<h2>Ce qui a été dit, ce qui a été voté.</h2>
		</div>
		<a href="/ecarts" class="see-all"><Mono color="var(--accent)">Voir tous les écarts (314) →</Mono></a>
	</div>
	<div class="ecarts-grid">
		{#each ecarts as e (e.id)}
			<article class="ecart-card">
				<div class="ecart-photo" aria-hidden="true"></div>
				<div class="ecart-body">
					<div class="ecart-who">
						<div>
							<h4>{e.depute_nom}</h4>
							{#if e.role}<Mono>{e.role}</Mono>{/if}
						</div>
						{#if e.groupe_acronyme}
							<PartyTag acronym={e.groupe_acronyme} />
						{/if}
					</div>
					<div class="ecart-said">
						<Mono>Ce qui a été dit</Mono>
						<p class="quote">{e.quote_said}</p>
						{#if e.quote_said_when}<Mono>{e.quote_said_when}</Mono>{/if}
					</div>
					<div class="ecart-voted">
						<Mono color="var(--accent)">Ce qui a été voté</Mono>
						<p class="voted-label">{e.vote_label}</p>
						{#if e.vote_when}<Mono>{e.vote_when}</Mono>{/if}
					</div>
				</div>
			</article>
		{/each}
	</div>
</section>
{/if}

<!-- ── THÈMES ─────────────────────────────────────────────────────────────── -->
{#if themes.length > 0}
<section class="themes-section">
	<div class="section-header">
		<h2>Explorer par thème</h2>
		<a href="/themes" class="see-all"><Mono color="var(--accent)">Tous les thèmes →</Mono></a>
	</div>
	<div class="themes-grid">
		{#each themes as t (t.slug)}
			<a href="/themes/{t.slug}" class="theme-cell">
				<span class="theme-nom">{t.nom}</span>
				<Mono color="var(--accent)">{t.nb_scrutins} scrutins documentés →</Mono>
			</a>
		{/each}
	</div>
</section>
{/if}

<!-- ── NEWSLETTER ─────────────────────────────────────────────────────────── -->
<section class="newsletter-section">
	<div class="nl-grid">
		<div>
			<Mono color="var(--accent-soft)">Recevoir l'édition hebdomadaire</Mono>
			<h2>Une lettre, <em>chaque vendredi</em>.<br/>Trois écarts, trois scrutins, une analyse.</h2>
			<p>Gratuit, sans publicité, livré sans intermédiaires. Désabonnement en un clic.</p>
		</div>
		<div class="nl-form">
			<div class="nl-input-row">
				<input type="email" placeholder="votre@email.fr" aria-label="Adresse e-mail" />
				<button type="button">S'inscrire</button>
			</div>
			<Mono>3 412 abonnés · taux d'ouverture moyen : 67 %</Mono>
		</div>
	</div>
</section>

<style>
	/* ── Hero ─────────────────────────────────────────────────────────── */
	.hero {
		padding: 60px var(--page-pad-x) 40px;
		border-bottom: 1px solid var(--rule);
	}

	.hero h1 {
		font-size: clamp(48px, 7vw, 84px);
		font-weight: 400;
		line-height: 1;
		letter-spacing: -0.025em;
		margin: 20px 0 0;
		max-width: 1100px;
	}

	.hero h1 em {
		color: var(--accent);
		font-style: italic;
	}

	.hero-lede {
		font-family: var(--font-serif);
		font-size: clamp(18px, 2vw, 26px);
		font-style: italic;
		line-height: 1.35;
		color: var(--muted);
		margin: 24px 0 0;
		max-width: 900px;
	}

	.hero-stats {
		margin-top: 36px;
		display: flex;
		flex-wrap: wrap;
		gap: 12px 28px;
		font-family: var(--font-mono);
		font-size: 13px;
		color: var(--muted);
		letter-spacing: 0.04em;
	}

	.hero-stats strong {
		color: var(--ink);
	}

	.hero-stats .sep {
		color: var(--rule);
	}

	.hero-stats .accent strong {
		color: var(--accent);
	}

	.error-msg {
		color: var(--contre);
		margin-top: 12px;
		font-size: 14px;
	}

	/* ── Hémicycle ────────────────────────────────────────────────────── */
	.hemicycle-section {
		padding: var(--section-pad-y) var(--page-pad-x);
		background: var(--paper);
		border-bottom: 1px solid var(--rule);
	}

	.hemicycle-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 56px;
		align-items: center;
	}

	.hemicycle-text h2 {
		font-size: clamp(28px, 3.5vw, 42px);
		font-weight: 500;
		line-height: 1.1;
		letter-spacing: -0.015em;
		margin: 16px 0;
	}

	.hemicycle-text h2 em {
		color: var(--accent);
		font-style: italic;
	}

	.hemicycle-text p {
		font-size: 18px;
		line-height: 1.55;
		color: var(--ink-soft);
		margin: 0 0 24px;
		max-width: 460px;
	}

	.group-legend {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0;
	}

	.legend-row {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 4px 0;
		border-bottom: 1px dotted var(--rule);
		font-family: var(--font-mono);
		font-size: 13px;
		text-decoration: none;
		color: inherit;
	}

	.legend-row:hover { background: var(--bg-alt); }

	.dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
	.acro { color: var(--ink); font-weight: 600; }
	.gnom { color: var(--muted); font-size: 12px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.gcnt { color: var(--ink); font-weight: 600; }

	.hemicycle-svg {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
	}

	/* ── Scrutins ─────────────────────────────────────────────────────── */
	.scrutins-section {
		padding: var(--section-pad-y) var(--page-pad-x);
		border-bottom: 1px solid var(--rule);
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		margin-bottom: 24px;
	}

	.section-header h2 {
		font-size: clamp(24px, 2.5vw, 36px);
		font-weight: 500;
		margin: 0;
	}

	.see-all { text-decoration: none; }

	.scrutins-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 15px;
	}

	.scrutins-table thead tr {
		border-bottom: 2px solid var(--ink);
	}

	.scrutins-table th {
		text-align: left;
		padding: 10px 14px;
		font-family: var(--font-mono);
		font-size: 11px;
		font-weight: 600;
		color: var(--muted);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.scrutins-table tbody tr {
		border-bottom: 1px solid var(--rule);
	}

	.scrutins-table td {
		padding: 14px;
		vertical-align: middle;
	}

	.scrutins-table .num a {
		font-family: var(--font-mono);
		color: var(--accent);
		font-weight: 600;
		text-decoration: none;
	}

	.scrutins-table .titre {
		font-family: var(--font-serif);
		font-size: 18px;
		font-weight: 500;
		max-width: 540px;
	}

	.scrutins-table .titre a {
		color: var(--ink);
		text-decoration: none;
	}

	.scrutins-table .titre a:hover {
		text-decoration: underline;
		text-decoration-color: var(--rule);
	}

	.scrutins-table .date {
		font-family: var(--font-mono);
		font-size: 12px;
		color: var(--muted);
		white-space: nowrap;
	}

	.scrutins-table .bar-cell { min-width: 180px; }

	.vote-num {
		font-family: var(--font-mono);
		font-weight: 600;
	}

	.vote-num.pour   { color: var(--pour); }
	.vote-num.contre { color: var(--contre); }
	.vote-num.abst   { color: var(--abst); }

	/* ── Écarts ───────────────────────────────────────────────────────── */
	.ecarts-section {
		padding: var(--section-pad-y) var(--page-pad-x);
		background: var(--bg-alt);
		border-bottom: 1px solid var(--rule);
	}

	.ecarts-section .section-header {
		margin-bottom: 28px;
		align-items: flex-start;
	}

	.ecarts-section h2 {
		font-size: clamp(24px, 2.5vw, 36px);
		font-weight: 500;
		margin: 14px 0 0;
	}

	.ecarts-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 28px;
	}

	.ecart-card {
		background: var(--bg);
		border: 1px solid var(--rule);
		padding: 28px;
		display: grid;
		grid-template-columns: 60px 1fr;
		gap: 20px;
	}

	.ecart-photo {
		width: 60px;
		height: 72px;
		background: repeating-linear-gradient(45deg, var(--bg-alt), var(--bg-alt) 6px, #ddd8c9 6px, #ddd8c9 12px);
		border: 1px solid var(--muted);
		flex-shrink: 0;
	}

	.ecart-who {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 12px;
	}

	.ecart-who h4 {
		font-family: var(--font-serif);
		font-size: 22px;
		font-weight: 500;
		margin: 0;
	}

	.ecart-said,
	.ecart-voted {
		margin-top: 14px;
		padding-top: 14px;
		border-top: 1px dotted var(--rule);
	}

	.quote {
		font-family: var(--font-serif);
		font-style: italic;
		font-size: 16px;
		line-height: 1.4;
		color: var(--ink);
		margin: 4px 0;
	}

	.voted-label {
		font-family: var(--font-serif);
		font-weight: 500;
		font-size: 17px;
		line-height: 1.3;
		color: var(--ink);
		margin: 4px 0;
	}

	/* ── Thèmes ───────────────────────────────────────────────────────── */
	.themes-section {
		padding: var(--section-pad-y) var(--page-pad-x);
		border-bottom: 1px solid var(--rule);
	}

	.themes-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		border-top: 1px solid var(--ink);
		border-left: 1px solid var(--rule);
	}

	.theme-cell {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 24px 20px;
		border-right: 1px solid var(--rule);
		border-bottom: 1px solid var(--rule);
		text-decoration: none;
		transition: background 0.15s;
	}

	.theme-cell:hover { background: var(--bg-alt); }

	.theme-nom {
		font-family: var(--font-serif);
		font-size: 22px;
		font-weight: 500;
		color: var(--ink);
	}

	/* ── Newsletter ───────────────────────────────────────────────────── */
	.newsletter-section {
		padding: 60px var(--page-pad-x);
		background: var(--ink);
		color: var(--bg);
	}

	.nl-grid {
		display: grid;
		grid-template-columns: 1.4fr 1fr;
		gap: 56px;
		align-items: center;
	}

	.newsletter-section h2 {
		font-size: clamp(28px, 3.5vw, 48px);
		font-weight: 400;
		line-height: 1.1;
		letter-spacing: -0.02em;
		margin: 12px 0 16px;
		color: var(--bg);
	}

	.newsletter-section h2 em {
		color: var(--accent-soft);
		font-style: italic;
	}

	.newsletter-section p {
		font-size: 18px;
		line-height: 1.5;
		color: #cfcbc0;
		margin: 0;
	}

	.nl-form {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.nl-input-row {
		display: flex;
		border: 1px solid var(--bg);
	}

	.nl-input-row input {
		flex: 1;
		padding: 14px 16px;
		background: transparent;
		border: none;
		outline: none;
		color: var(--bg);
		font-family: var(--font-mono);
		font-size: 14px;
	}

	.nl-input-row input::placeholder { color: rgba(255,255,255,0.4); }

	.nl-input-row button {
		background: var(--accent);
		color: var(--bg);
		border: none;
		padding: 14px 24px;
		font-family: var(--font-mono);
		font-size: 12px;
		font-weight: 600;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		cursor: pointer;
	}

	/* ── Responsive ───────────────────────────────────────────────────── */
	@media (max-width: 1024px) {
		.hemicycle-grid { grid-template-columns: 1fr; }
		.hemicycle-text p { max-width: none; }
		.ecarts-grid { grid-template-columns: 1fr; }
		.themes-grid { grid-template-columns: repeat(2, 1fr); }
		.nl-grid { grid-template-columns: 1fr; gap: 32px; }
	}

	@media (max-width: 640px) {
		.themes-grid { grid-template-columns: 1fr 1fr; }
		.scrutins-table { font-size: 13px; }
		.scrutins-table .bar-cell { display: none; }
		.group-legend { grid-template-columns: 1fr; }
	}
</style>
