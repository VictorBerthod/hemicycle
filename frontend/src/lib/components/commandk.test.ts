import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import CommandK from './CommandK.svelte';

// Mock the API module
vi.mock('$lib/api', () => ({
	search: vi.fn().mockResolvedValue({
		deputes: [
			{ uid: 'PA001', prenom: 'Jean', nom: 'Dupont', groupe: { acronyme: 'LFI', nom: 'La France insoumise', id: 1, slug: 'lfi', couleur: null }, slug: 'jean-dupont', photo_url: null, circo_departement: 'Paris', circo_numero: 1 },
		],
		scrutins: [
			{ id: 1, numero: 100, titre: 'Loi climat', date_scrutin: '2026-05-01', sort: 'adopte', nb_pour: 300, nb_contre: 200, nb_abstention: 50, nb_votants: 550 },
		],
	}),
}));

vi.mock('$lib/tokens', () => ({
	getGroupColor: () => '#c12c44',
}));

describe('CommandK', () => {
	const noop = () => {};

	it('does not render when open=false', () => {
		const { container } = render(CommandK, { props: { open: false, onClose: noop } });
		expect(container.querySelector('[role="dialog"]')).toBeNull();
	});

	it('renders dialog when open=true', () => {
		render(CommandK, { props: { open: true, onClose: noop } });
		expect(screen.getByRole('dialog')).toBeTruthy();
	});

	it('shows hint text before typing', () => {
		render(CommandK, { props: { open: true, onClose: noop } });
		expect(screen.getByText(/Tapez au moins 2 caractères/)).toBeTruthy();
	});

	it('has an accessible search input', () => {
		render(CommandK, { props: { open: true, onClose: noop } });
		const input = screen.getByRole('searchbox', { name: 'Recherche' });
		expect(input).toBeTruthy();
	});

	it('calls onClose when Escape is pressed on backdrop', () => {
		const onClose = vi.fn();
		render(CommandK, { props: { open: true, onClose } });
		const dialog = screen.getByRole('dialog');
		fireEvent.keyDown(dialog, { key: 'Escape' });
		expect(onClose).toHaveBeenCalledOnce();
	});

	it('calls onClose when close button is clicked', () => {
		const onClose = vi.fn();
		render(CommandK, { props: { open: true, onClose } });
		const closeBtn = screen.getByRole('button', { name: 'Fermer' });
		fireEvent.click(closeBtn);
		expect(onClose).toHaveBeenCalledOnce();
	});

	it('has aria-modal=true on dialog', () => {
		render(CommandK, { props: { open: true, onClose: noop } });
		const dialog = screen.getByRole('dialog');
		expect(dialog.getAttribute('aria-modal')).toBe('true');
	});

	it('has a results listbox', () => {
		render(CommandK, { props: { open: true, onClose: noop } });
		expect(screen.getByRole('listbox')).toBeTruthy();
	});
});
