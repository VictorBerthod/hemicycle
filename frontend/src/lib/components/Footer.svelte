<script lang="ts">
	/**
	 * Footer — pied de page éditorial.
	 * Référence : design_handoff_nsv_politique/mockups/mockups/shared.jsx (Footer).
	 */

	const COLUMNS: { title: string; items: { label: string; href: string }[] }[] = [
		{
			title: 'Explorer',
			items: [
				{ label: 'Personnalités', href: '/personnalites' },
				{ label: 'Scrutins récents', href: '/scrutins' },
				{ label: 'Comparateur', href: '/comparateur' },
				{ label: 'Index thématique', href: '/themes' },
			],
		},
		{
			title: 'Méthode',
			items: [
				{ label: 'Notre méthodologie', href: '/methode' },
				{ label: 'Sources de données', href: '/methode#sources' },
				{ label: 'Faux positifs', href: '/methode#faux-positifs' },
				{ label: 'Droit de réponse', href: '/droit-de-reponse' },
			],
		},
		{
			title: 'Éditorial',
			items: [
				{ label: 'Enquêtes', href: '/enquetes' },
				{ label: 'Newsletter', href: '/newsletter' },
				{ label: "Notes d'analyse", href: '/notes' },
				{ label: 'À propos', href: '/a-propos' },
			],
		},
		{
			title: 'Contribuer',
			items: [
				{ label: 'Repository', href: 'https://github.com/VictorBerthod/hemicycle' },
				{ label: 'Dons', href: '/dons' },
				{ label: 'Devenir bénévole', href: '/benevolat' },
				{ label: 'Signaler une erreur', href: '/signaler' },
			],
		},
	];
</script>

<footer class="footer">
	<div class="grid">
		<div class="brand">
			<div class="logo">
				<span>[PROJET]</span><span class="logo-tld">.fr</span>
			</div>
			<p class="tagline">
				Confronter le discours public à l'acte législatif. Sourcé, contextualisé, réfutable.
			</p>
		</div>

		{#each COLUMNS as col (col.title)}
			<div class="col">
				<h4 class="col-title">{col.title}</h4>
				<ul>
					{#each col.items as item (item.label)}
						<li>
							<a href={item.href}>{item.label}</a>
						</li>
					{/each}
				</ul>
			</div>
		{/each}
	</div>

	<div class="copyright">
		<span>© 2026 [PROJET] · Données : Assemblée nationale · Sénat · HATVP · Vie-publique.fr</span>
		<span>Licence Etalab 2.0 · <a href="https://github.com/VictorBerthod/hemicycle">Code source GitHub</a></span>
	</div>
</footer>

<style>
	.footer {
		border-top: 4px solid var(--ink);
		margin-top: 80px;
		padding: 40px var(--page-pad-x) 32px;
		background: var(--bg-alt);
	}

	.grid {
		display: grid;
		grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr;
		gap: 40px;
		padding-bottom: 32px;
		border-bottom: 1px solid var(--rule);
	}

	.brand .logo {
		font-family: var(--font-serif);
		font-size: 26px;
		font-weight: 600;
		color: var(--ink);
		letter-spacing: -0.01em;
	}

	.brand .logo-tld {
		color: var(--accent);
		font-style: italic;
		font-weight: 500;
	}

	.tagline {
		font-family: var(--font-serif);
		font-style: italic;
		font-size: 17px;
		line-height: 1.4;
		color: var(--ink-soft);
		margin-top: 12px;
		max-width: 280px;
	}

	.col-title {
		font-family: var(--font-mono);
		font-size: 12px;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--ink);
		margin-bottom: 12px;
	}

	.col ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.col li {
		font-size: 14px;
		color: var(--ink-soft);
	}

	.col a {
		color: var(--ink-soft);
		text-decoration: none;
		transition: color 0.15s;
	}

	.col a:hover {
		color: var(--ink);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 3px;
	}

	.copyright {
		margin-top: 20px;
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		color: var(--muted);
		display: flex;
		justify-content: space-between;
		gap: 16px;
		flex-wrap: wrap;
	}

	.copyright a {
		color: var(--muted);
		text-decoration: underline;
		text-decoration-color: var(--rule);
	}

	.copyright a:hover {
		color: var(--ink);
	}

	@media (max-width: 1024px) {
		.grid {
			grid-template-columns: 1fr 1fr 1fr;
		}
		.brand {
			grid-column: 1 / -1;
		}
	}

	@media (max-width: 640px) {
		.grid {
			grid-template-columns: 1fr 1fr;
			gap: 24px;
		}
		.copyright {
			flex-direction: column;
			gap: 8px;
		}
	}
</style>
