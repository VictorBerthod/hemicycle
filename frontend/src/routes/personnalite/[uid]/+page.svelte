<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { getDepute, getDissidences, type DeputeDetail, type DissidenceResult } from '$lib/api';
	import { getGroupColor } from '$lib/tokens';
	import PartyTag from '$lib/components/PartyTag.svelte';
	import VoteBadge from '$lib/components/VoteBadge.svelte';
	import VoteBar from '$lib/components/VoteBar.svelte';
	import Eyebrow from '$lib/components/Eyebrow.svelte';
	import Mono from '$lib/components/Mono.svelte';
	import Placeholder from '$lib/components/Placeholder.svelte';

	type Tab = 'overview' | 'votes' | 'dissidences';

	let depute = $state<DeputeDetail | null>(null);
	let dissidences = $state<DissidenceResult | null>(null);
	let loading = $state(true);
	let error = $state('');
	let activeTab = $state<Tab>('overview');

	let uid = $derived(page.params.uid ?? '');

	onMount(async () => {
		if (!uid) { error = 'Identifiant manquant.'; loading = false; return; }
		try {
			const [d, dis] = await Promise.all([
				getDepute(uid),
				getDissidences(uid),
			]);
			depute = d;
			dissidences = dis;
		} catch {
			error = 'Impossible de charger cette fiche. Vérifiez que le backend est en marche.';
		} finally {
			loading = false;
		}
	});

	function formatDate(d: string) {
		return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
	}

	function formatDateShort(d: string) {
		return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
	}

	let participationPct = $derived(
		dissidences && dissidences.total_votes > 0
			? Math.round((dissidences.total_votes / 600) * 100) // rough estimate vs total scrutins
			: null
	);

	let coherencePct = $derived(
		dissidences
			? Math.round(100 - dissidences.taux_dissidence)
			: null
	);
</script>

<svelte:head>
	{#if depute}
		<title>{depute.prenom} {depute.nom} — [PROJET].fr</title>
	{:else}
		<title>Fiche personnalité — [PROJET].fr</title>
	{/if}
</svelte:head>

<!-- ── BREADCRUMB ─────────────────────────────────────────────────────────── -->
<nav class="breadcrumb" aria-label="Fil d'Ariane">
	<a href="/personnalites">Personnalités</a>
	<span class="sep" aria-hidden="true">/</span>
	<span>17ᵉ législature</span>
	<span class="sep" aria-hidden="true">/</span>
	{#if depute}
		<span class="current">{depute.prenom} {depute.nom}</span>
	{:else}
		<Placeholder width="160px" height="14px" inline />
	{/if}
</nav>

{#if error}
	<div class="error-state">
		<p>{error}</p>
		<a href="/personnalites">← Retour à l'annuaire</a>
	</div>
{:else if loading}
	<!-- Skeleton header -->
	<header class="fiche-header">
		<div class="header-grid">
			<Placeholder width="180px" height="220px" />
			<div class="identity">
				<Placeholder width="240px" height="14px" />
				<Placeholder width="400px" height="64px" />
				<Placeholder width="280px" height="30px" />
			</div>
			<div class="score-panel">
				<Placeholder width="100%" height="200px" />
			</div>
		</div>
	</header>
{:else if depute}
	<!-- ── HEADER ──────────────────────────────────────────────────────────── -->
	<header class="fiche-header">
		<div class="header-grid">
			<!-- Photo -->
			{#if depute.photo_url}
				<img src={depute.photo_url} alt="{depute.prenom} {depute.nom}" class="fiche-photo" />
			{:else}
				<div class="fiche-photo placeholder-photo" aria-hidden="true">
					<Mono>Portrait · placeholder</Mono>
				</div>
			{/if}

			<!-- Identité -->
			<div class="identity">
				<Mono color="var(--accent)">Député{depute.sexe === 'F' ? 'e' : ''} · 17ᵉ législature{depute.date_mandat_debut ? ' · élu' + (depute.sexe === 'F' ? 'e' : '') + ' ' + new Date(depute.date_mandat_debut).getFullYear() : ''}</Mono>
				<h1>{depute.prenom} <em>{depute.nom}</em></h1>
				<div class="identity-tags">
					{#if depute.groupe}
						<PartyTag acronym={depute.groupe.acronyme} label={depute.groupe.nom} size="md" />
					{/if}
				</div>
				<div class="identity-grid">
					{#if depute.circo_departement}
						<Mono>Circonscription</Mono>
						<span>{depute.circo_departement}{depute.circo_numero ? ` · ${depute.circo_numero}ᵉ circonscription` : ''}</span>
					{/if}
					{#if depute.date_naissance}
						<Mono>Né·e le</Mono>
						<span>{formatDate(depute.date_naissance)}</span>
					{/if}
					{#if depute.url_an}
						<Mono>Source officielle</Mono>
						<a href={depute.url_an} target="_blank" rel="noopener" class="link-an">assemblee-nationale.fr →</a>
					{/if}
				</div>
			</div>

			<!-- Score panel -->
			<aside class="score-panel">
				<Mono>Densité documentée</Mono>
				<div class="score-main">
					<span class="score-num">{dissidences?.dissidences.length ?? '—'}</span>
					<span class="score-desc">dissidences documentées depuis l'élection.</span>
				</div>
				<div class="score-stats">
					{#if coherencePct !== null}
					<div class="stat-mini">
						<Mono>Cohérence groupe</Mono>
						<div class="stat-mini-val">{coherencePct} <span class="unit">%</span></div>
					</div>
					{/if}
					{#if dissidences}
					<div class="stat-mini">
						<Mono>Votes suivis</Mono>
						<div class="stat-mini-val">{dissidences.total_votes}</div>
					</div>
					{/if}
				</div>
			</aside>
		</div>
	</header>

	<!-- ── ONGLETS ────────────────────────────────────────────────────────── -->
	<nav class="tab-nav" aria-label="Sections de la fiche">
		{#each [
			{ key: 'overview' as Tab, label: "Vue d'ensemble" },
			{ key: 'votes' as Tab, label: 'Votes', count: dissidences?.total_votes },
			{ key: 'dissidences' as Tab, label: 'Dissidences', count: dissidences?.dissidences.length },
		] as tab (tab.key)}
			<button
				class="tab-btn"
				class:active={activeTab === tab.key}
				onclick={() => activeTab = tab.key}
				type="button"
			>
				{tab.label}
				{#if tab.count !== undefined && tab.count !== null}
					<span class="tab-count" class:active={activeTab === tab.key}>{tab.count}</span>
				{/if}
			</button>
		{/each}
	</nav>

	<!-- ── VUE D'ENSEMBLE ─────────────────────────────────────────────────── -->
	{#if activeTab === 'overview'}

	<!-- Discipline + Trajectoire -->
	{#if dissidences}
	<section class="discipline-section">
		<div class="discipline-grid">
			<!-- Discipline -->
			<div>
				<Eyebrow>Discipline de vote · 17ᵉ législature</Eyebrow>
				<h3>
					Aligne le groupe {coherencePct}&#8239;% du temps.
					{dissidences.dissidences.length} vote{dissidences.dissidences.length !== 1 ? 's' : ''} dissident{dissidences.dissidences.length !== 1 ? 's' : ''} documenté{dissidences.dissidences.length !== 1 ? 's' : ''}.
				</h3>
				{#if depute.groupe}
				<div class="discipline-bar-wrap">
					<div class="discipline-bar">
						<div class="segment aligned" style:width="{coherencePct}%"></div>
						<div class="segment dissident" style:width="{dissidences.taux_dissidence}%"></div>
					</div>
					<div class="discipline-legend">
						<span>{dissidences.total_votes - dissidences.dissidences.length} votes alignés sur la consigne {depute.groupe.acronyme}</span>
						<span>{dissidences.dissidences.length} votes dissidents</span>
					</div>
				</div>
				{/if}

				{#if dissidences.dissidences.length > 0}
				<ul class="dissidences-list">
					{#each dissidences.dissidences.slice(0, 5) as d (d.scrutin_numero)}
						<li class="dissidence-item">
							<a href="/scrutin/{d.scrutin_numero}" class="diss-ref"><Mono color="var(--accent)">n°{d.scrutin_numero}</Mono></a>
							<span class="diss-titre">{d.scrutin_titre}</span>
							<Mono>a voté {d.depute_position}, groupe {d.groupe_position}</Mono>
						</li>
					{/each}
				</ul>
				{/if}
			</div>

			<!-- Votes récents mini -->
			<div>
				<Eyebrow>Votes récents</Eyebrow>
				<h3>Dernières positions nominales.</h3>
				<table class="mini-votes-table">
					<thead>
						<tr>
							{#each ['Date', 'Scrutin', 'Position', 'Résultat'] as h (h)}
								<th>{h}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each depute.recent_votes.slice(0, 6) as v (v.scrutin_numero)}
							<tr>
								<td class="v-date">{formatDateShort(v.scrutin_date)}</td>
								<td class="v-titre">
									<a href="/scrutin/{v.scrutin_numero}">n°{v.scrutin_numero} · {v.scrutin_titre.length > 50 ? v.scrutin_titre.slice(0, 50) + '…' : v.scrutin_titre}</a>
								</td>
								<td><VoteBadge position={v.position === 'pour' ? 'pour' : v.position === 'contre' ? 'contre' : v.position === 'abstention' ? 'abst' : 'absent'} /></td>
								<td><VoteBadge position={v.scrutin_sort === 'adopte' ? 'adopte' : 'rejete'} /></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	</section>
	{/if}

	<!-- ── VOTES (onglet) ─────────────────────────────────────────────────── -->
	{:else if activeTab === 'votes'}
	<section class="votes-section">
		<div class="section-header">
			<h2>Votes nominaux</h2>
		</div>
		<table class="votes-table">
			<thead>
				<tr>
					{#each ['Date', 'Scrutin', 'Position', 'Résultat loi'] as h (h)}
						<th>{h}</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each depute.recent_votes as v (v.scrutin_numero)}
					<tr>
						<td class="v-date">{formatDate(v.scrutin_date)}</td>
						<td class="v-titre">
							<a href="/scrutin/{v.scrutin_numero}">n°{v.scrutin_numero} · {v.scrutin_titre}</a>
						</td>
						<td><VoteBadge position={v.position === 'pour' ? 'pour' : v.position === 'contre' ? 'contre' : v.position === 'abstention' ? 'abst' : 'absent'} /></td>
						<td><VoteBadge position={v.scrutin_sort === 'adopte' ? 'adopte' : 'rejete'} /></td>
					</tr>
				{/each}
			</tbody>
		</table>
	</section>

	<!-- ── DISSIDENCES (onglet) ───────────────────────────────────────────── -->
	{:else if activeTab === 'dissidences'}
	<section class="diss-section">
		<div class="section-header">
			<div>
				<Eyebrow>Votes contre la consigne du groupe</Eyebrow>
				<h2>Taux de dissidence : {dissidences?.taux_dissidence ?? '—'}&#8239;%</h2>
			</div>
		</div>
		{#if dissidences && dissidences.dissidences.length > 0}
			<div class="diss-full-list">
				{#each dissidences.dissidences as d (d.scrutin_numero)}
					<article class="diss-row">
						<div class="diss-meta">
							<a href="/scrutin/{d.scrutin_numero}" class="diss-ref-link">
								<Mono color="var(--accent)">n°{d.scrutin_numero}</Mono>
							</a>
							<Mono>{d.scrutin_date}</Mono>
						</div>
						<p class="diss-titre-full">{d.scrutin_titre}</p>
						<div class="diss-positions">
							<div>
								<Mono>Ce député</Mono>
								<VoteBadge position={d.depute_position === 'pour' ? 'pour' : d.depute_position === 'contre' ? 'contre' : d.depute_position === 'abstention' ? 'abst' : 'absent'} />
							</div>
							<div>
								<Mono>Majorité groupe</Mono>
								<VoteBadge position={d.groupe_position === 'pour' ? 'pour' : d.groupe_position === 'contre' ? 'contre' : d.groupe_position === 'abstention' ? 'abst' : 'absent'} />
							</div>
						</div>
					</article>
				{/each}
			</div>
		{:else}
			<div class="empty-state">
				<Mono>Aucune dissidence documentée.</Mono>
			</div>
		{/if}
	</section>
	{/if}

	<!-- ── METHODOLOGIE ───────────────────────────────────────────────────── -->
	<section class="methodo-section">
		<div class="methodo-grid">
			<div>
				<Mono color="var(--ink)">Méthodologie · fiche</Mono>
				<p>
					Cette fiche agrège les votes nominaux publiés par l'Assemblée nationale et les prises
					de parole publiques sourcées (plateaux, tribunes, communiqués, comptes officiels).
					Chaque écart est validé par deux relecteurs avant publication.
				</p>
				<a href="/methode" class="methodo-link"><Mono color="var(--accent)">Lire la méthodologie →</Mono></a>
			</div>
			<div>
				<Mono color="var(--ink)">Droit de réponse</Mono>
				<p>
					Cette fiche est ouverte au droit de réponse de la personnalité concernée et de son équipe.
					Toute réponse publiée est rattachée à l'écart concerné, sans modification du fait initial.
				</p>
				<a href="/droit-de-reponse" class="methodo-link"><Mono color="var(--accent)">Déposer une réponse →</Mono></a>
			</div>
		</div>
	</section>
{/if}

<style>
	/* ── Breadcrumb ───────────────────────────────────────────────────── */
	.breadcrumb {
		padding: 14px var(--page-pad-x);
		border-bottom: 1px solid var(--rule);
		font-family: var(--font-mono);
		font-size: 12px;
		color: var(--muted);
		letter-spacing: 0.04em;
		display: flex;
		align-items: center;
		gap: 0;
		flex-wrap: wrap;
	}

	.breadcrumb a { color: var(--muted); text-decoration: none; }
	.breadcrumb a:hover { color: var(--ink); }
	.breadcrumb .sep { margin: 0 8px; }
	.breadcrumb .current { color: var(--ink); }

	/* ── Header ───────────────────────────────────────────────────────── */
	.fiche-header {
		padding: 48px var(--page-pad-x) 40px;
		border-bottom: 1px solid var(--ink);
	}

	.header-grid {
		display: grid;
		grid-template-columns: 180px 1fr 320px;
		gap: 40px;
		align-items: flex-start;
	}

	.fiche-photo {
		width: 180px;
		height: 220px;
		object-fit: cover;
		display: block;
	}

	.placeholder-photo {
		width: 180px;
		height: 220px;
		background: repeating-linear-gradient(45deg, var(--bg-alt), var(--bg-alt) 10px, #ddd8c9 10px, #ddd8c9 20px);
		border: 1px solid var(--muted);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.identity h1 {
		font-family: var(--font-serif);
		font-size: clamp(36px, 5vw, 64px);
		font-weight: 500;
		line-height: 1;
		letter-spacing: -0.02em;
		margin: 14px 0;
	}

	.identity h1 em {
		color: var(--accent);
		font-style: normal;
	}

	.identity-tags {
		display: flex;
		gap: 12px;
		align-items: center;
		flex-wrap: wrap;
		margin-bottom: 18px;
	}

	.identity-grid {
		display: grid;
		grid-template-columns: auto 1fr;
		column-gap: 18px;
		row-gap: 6px;
		font-size: 14px;
		max-width: 580px;
	}

	.link-an {
		color: var(--accent);
		font-size: 13px;
	}

	/* Score panel */
	.score-panel {
		background: var(--paper);
		border: 1px solid var(--rule);
		padding: 24px;
		display: flex;
		flex-direction: column;
		gap: 18px;
	}

	.score-main {
		display: flex;
		align-items: baseline;
		gap: 10px;
	}

	.score-num {
		font-family: var(--font-serif);
		font-size: 72px;
		font-weight: 400;
		line-height: 0.9;
		color: var(--accent);
	}

	.score-desc {
		font-size: 13px;
		color: var(--muted);
		max-width: 180px;
		line-height: 1.4;
	}

	.score-stats {
		border-top: 1px solid var(--rule);
		padding-top: 14px;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 14px;
	}

	.stat-mini { display: flex; flex-direction: column; gap: 4px; }

	.stat-mini-val {
		font-family: var(--font-serif);
		font-size: 26px;
		font-weight: 500;
	}

	.unit { font-size: 13px; color: var(--muted); }

	/* ── Onglets ──────────────────────────────────────────────────────── */
	.tab-nav {
		padding: 0 var(--page-pad-x);
		border-bottom: 1px solid var(--rule);
		display: flex;
		gap: 36px;
	}

	.tab-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 16px 0;
		background: none;
		border: none;
		border-bottom: 2px solid transparent;
		font-family: var(--font-sans);
		font-size: 15px;
		font-weight: 500;
		color: var(--ink);
		cursor: pointer;
		transition: color 0.15s, border-color 0.15s;
	}

	.tab-btn.active {
		color: var(--accent);
		border-bottom-color: var(--accent);
	}

	.tab-count {
		font-size: 11px;
		padding: 2px 7px;
		background: var(--bg-alt);
		color: var(--muted);
		font-family: var(--font-mono);
		font-weight: 600;
	}

	.tab-count.active {
		background: var(--accent);
		color: var(--bg);
	}

	/* ── Discipline ───────────────────────────────────────────────────── */
	.discipline-section {
		padding: var(--section-pad-y) var(--page-pad-x);
		border-bottom: 1px solid var(--rule);
	}

	.discipline-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 48px;
	}

	.discipline-section h3 {
		font-family: var(--font-serif);
		font-size: 22px;
		font-weight: 500;
		margin: 12px 0 18px;
		line-height: 1.3;
	}

	.discipline-bar-wrap {
		margin-bottom: 20px;
	}

	.discipline-bar {
		display: flex;
		height: 28px;
		border: 1px solid var(--ink);
		overflow: hidden;
	}

	.segment.aligned   { background: var(--pour); }
	.segment.dissident { background: var(--contre); }

	.discipline-legend {
		display: flex;
		justify-content: space-between;
		margin-top: 10px;
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.04em;
		color: var(--muted);
	}

	.dissidences-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.dissidence-item {
		display: grid;
		grid-template-columns: 90px 1fr auto;
		gap: 14px;
		align-items: baseline;
		padding-bottom: 10px;
		border-bottom: 1px dotted var(--rule);
	}

	.diss-ref { text-decoration: none; }
	.diss-titre { font-family: var(--font-serif); font-size: 16px; }

	/* Mini votes table */
	.mini-votes-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 13px;
	}

	.mini-votes-table th {
		text-align: left;
		padding: 8px 10px;
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 600;
		color: var(--muted);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		border-bottom: 2px solid var(--ink);
	}

	.mini-votes-table td {
		padding: 10px;
		border-bottom: 1px solid var(--rule);
		vertical-align: middle;
	}

	.v-date { font-family: var(--font-mono); font-size: 11px; color: var(--muted); white-space: nowrap; }
	.v-titre { font-family: var(--font-serif); font-size: 15px; }
	.v-titre a { color: var(--ink); text-decoration: none; }
	.v-titre a:hover { text-decoration: underline; text-decoration-color: var(--rule); }

	/* ── Votes tab ────────────────────────────────────────────────────── */
	.votes-section {
		padding: var(--section-pad-y) var(--page-pad-x);
		border-bottom: 1px solid var(--rule);
	}

	.votes-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 14px;
	}

	.votes-table th {
		text-align: left;
		padding: 10px 14px;
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 600;
		color: var(--muted);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		border-bottom: 2px solid var(--ink);
	}

	.votes-table td {
		padding: 12px 14px;
		border-bottom: 1px solid var(--rule);
		vertical-align: middle;
	}

	/* ── Dissidences tab ──────────────────────────────────────────────── */
	.diss-section {
		padding: var(--section-pad-y) var(--page-pad-x);
		border-bottom: 1px solid var(--rule);
	}

	.diss-full-list {
		display: flex;
		flex-direction: column;
		gap: 16px;
		margin-top: 24px;
	}

	.diss-row {
		display: grid;
		grid-template-columns: 160px 1fr 200px;
		gap: 24px;
		align-items: start;
		padding: 20px;
		background: var(--paper);
		border: 1px solid var(--rule);
	}

	.diss-meta {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.diss-ref-link { text-decoration: none; }

	.diss-titre-full {
		font-family: var(--font-serif);
		font-size: 17px;
		line-height: 1.4;
		margin: 0;
	}

	.diss-positions {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.diss-positions > div {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	/* ── Common ───────────────────────────────────────────────────────── */
	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		margin-bottom: 24px;
	}

	.section-header h2 {
		font-family: var(--font-serif);
		font-size: clamp(24px, 2.5vw, 36px);
		font-weight: 500;
		margin: 14px 0 0;
	}

	.empty-state {
		padding: 48px 0;
		text-align: center;
	}

	.error-state {
		padding: 60px var(--page-pad-x);
	}

	.error-state p { color: var(--contre); margin-bottom: 16px; }

	/* ── Méthodologie ─────────────────────────────────────────────────── */
	.methodo-section {
		padding: 40px var(--page-pad-x);
		background: var(--bg-alt);
	}

	.methodo-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 56px;
	}

	.methodo-section p {
		font-size: 15px;
		line-height: 1.6;
		color: var(--ink-soft);
		margin-top: 10px;
		max-width: 480px;
	}

	.methodo-link { display: inline-block; margin-top: 14px; text-decoration: none; }

	/* ── Responsive ───────────────────────────────────────────────────── */
	@media (max-width: 1024px) {
		.header-grid { grid-template-columns: 140px 1fr; }
		.score-panel { grid-column: 1 / -1; }
		.discipline-grid { grid-template-columns: 1fr; gap: 32px; }
		.methodo-grid { grid-template-columns: 1fr; gap: 32px; }
	}

	@media (max-width: 640px) {
		.header-grid { grid-template-columns: 100px 1fr; gap: 16px; }
		.fiche-photo, .placeholder-photo { width: 100px; height: 120px; }
		.score-num { font-size: 48px; }
		.diss-row { grid-template-columns: 1fr; }
		.dissidence-item { grid-template-columns: 80px 1fr; }
	}
</style>
