import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import VoteDot from './VoteDot.svelte';
import VoteBadge from './VoteBadge.svelte';
import VoteBar from './VoteBar.svelte';
import PartyTag from './PartyTag.svelte';
import Eyebrow from './Eyebrow.svelte';
import Mono from './Mono.svelte';
import Placeholder from './Placeholder.svelte';

// ── VoteDot ──────────────────────────────────────────────────────────────────

describe('VoteDot', () => {
	it('renders a span with role img', () => {
		render(VoteDot, { props: { position: 'pour' } });
		const dot = screen.getByRole('img', { name: 'pour' });
		expect(dot).toBeTruthy();
	});

	it('applies default size 12px', () => {
		render(VoteDot, { props: { position: 'pour' } });
		const dot = screen.getByRole('img', { name: 'pour' });
		expect(dot.style.width).toBe('12px');
		expect(dot.style.height).toBe('12px');
	});

	it('applies custom size', () => {
		render(VoteDot, { props: { position: 'contre', size: 20 } });
		const dot = screen.getByRole('img', { name: 'contre' });
		expect(dot.style.width).toBe('20px');
		expect(dot.style.height).toBe('20px');
	});

	it('adds absent class for absent position', () => {
		render(VoteDot, { props: { position: 'absent' } });
		const dot = screen.getByRole('img', { name: 'absent' });
		expect(dot.classList.contains('absent')).toBe(true);
	});

	it('does not add absent class for other positions', () => {
		render(VoteDot, { props: { position: 'pour' } });
		const dot = screen.getByRole('img', { name: 'pour' });
		expect(dot.classList.contains('absent')).toBe(false);
	});
});

// ── VoteBadge ────────────────────────────────────────────────────────────────

describe('VoteBadge', () => {
	it('renders default label for pour', () => {
		render(VoteBadge, { props: { position: 'pour' } });
		expect(screen.getByText('Pour')).toBeTruthy();
	});

	it('renders default label for contre', () => {
		render(VoteBadge, { props: { position: 'contre' } });
		expect(screen.getByText('Contre')).toBeTruthy();
	});

	it('renders default label for abst', () => {
		render(VoteBadge, { props: { position: 'abst' } });
		expect(screen.getByText('Abstention')).toBeTruthy();
	});

	it('renders default label for absent', () => {
		render(VoteBadge, { props: { position: 'absent' } });
		expect(screen.getByText('Absent')).toBeTruthy();
	});

	it('renders Adopté for adopte', () => {
		render(VoteBadge, { props: { position: 'adopte' } });
		expect(screen.getByText('Adopté')).toBeTruthy();
	});

	it('renders Rejeté for rejete', () => {
		render(VoteBadge, { props: { position: 'rejete' } });
		expect(screen.getByText('Rejeté')).toBeTruthy();
	});
});

// ── VoteBar ──────────────────────────────────────────────────────────────────

describe('VoteBar', () => {
	it('renders with aria-label', () => {
		render(VoteBar, { props: { pour: 300, contre: 200, abst: 50 } });
		const bar = screen.getByRole('generic', { name: /Pour 300/ });
		expect(bar).toBeTruthy();
	});

	it('applies default height 8px', () => {
		render(VoteBar, { props: { pour: 300, contre: 200, abst: 50 } });
		const bar = screen.getByRole('generic', { name: /Pour 300/ });
		expect(bar.style.height).toBe('8px');
	});

	it('applies custom height', () => {
		render(VoteBar, { props: { pour: 100, contre: 50, abst: 25, height: 12 } });
		const bar = screen.getByRole('generic', { name: /Pour 100/ });
		expect(bar.style.height).toBe('12px');
	});

	it('renders 3 segments when total > 0', () => {
		const { container } = render(VoteBar, { props: { pour: 300, contre: 200, abst: 50 } });
		const segs = container.querySelectorAll('.seg');
		expect(segs.length).toBe(3);
	});

	it('renders no segments when total is 0', () => {
		const { container } = render(VoteBar, { props: { pour: 0, contre: 0, abst: 0 } });
		const segs = container.querySelectorAll('.seg');
		expect(segs.length).toBe(0);
	});

	it('sizes pour segment proportionally', () => {
		const { container } = render(VoteBar, { props: { pour: 50, contre: 50, abst: 0 } });
		const pour = container.querySelector('.seg.pour') as HTMLElement;
		expect(pour.style.width).toBe('50%');
	});
});

// ── PartyTag ─────────────────────────────────────────────────────────────────

describe('PartyTag', () => {
	it('renders acronym', () => {
		render(PartyTag, { props: { acronym: 'LFI' } });
		expect(screen.getByText('LFI')).toBeTruthy();
	});

	it('renders label when provided', () => {
		render(PartyTag, { props: { acronym: 'LFI', label: 'La France insoumise' } });
		expect(screen.getByText('La France insoumise')).toBeTruthy();
	});

	it('does not render label when omitted', () => {
		render(PartyTag, { props: { acronym: 'RN' } });
		expect(screen.queryByText('Rassemblement National')).toBeNull();
	});

	it('applies sm class by default', () => {
		const { container } = render(PartyTag, { props: { acronym: 'LFI' } });
		const tag = container.querySelector('.party-tag');
		expect(tag?.classList.contains('sm')).toBe(true);
	});

	it('applies md class when size is md', () => {
		const { container } = render(PartyTag, { props: { acronym: 'LFI', size: 'md' } });
		const tag = container.querySelector('.party-tag');
		expect(tag?.classList.contains('md')).toBe(true);
	});

	it('applies group color as border-left', () => {
		const { container } = render(PartyTag, { props: { acronym: 'LFI' } });
		const tag = container.querySelector('.party-tag') as HTMLElement;
		// jsdom normalizes hex to rgb
		expect(tag.style.borderLeft).toContain('rgb(193, 44, 68)');
	});

	it('uses fallback grey for unknown acronym', () => {
		const { container } = render(PartyTag, { props: { acronym: 'ZZUNKNOWN' } });
		const tag = container.querySelector('.party-tag') as HTMLElement;
		expect(tag.style.borderLeft).toContain('rgb(136, 136, 136)');
	});
});

// ── Eyebrow ──────────────────────────────────────────────────────────────────

describe('Eyebrow', () => {
	it('renders the eyebrow wrapper', () => {
		const { container } = render(Eyebrow, { props: {} });
		expect(container.querySelector('.eyebrow')).toBeTruthy();
	});

	it('contains the decorative line element', () => {
		const { container } = render(Eyebrow, { props: {} });
		expect(container.querySelector('.line')).toBeTruthy();
	});

	it('decorative line is aria-hidden', () => {
		const { container } = render(Eyebrow, { props: {} });
		const line = container.querySelector('.line');
		expect(line?.getAttribute('aria-hidden')).toBe('true');
	});
});

// ── Mono ─────────────────────────────────────────────────────────────────────

describe('Mono', () => {
	it('applies mono-atom class', () => {
		const { container } = render(Mono, { props: {} });
		expect(container.querySelector('.mono-atom')).toBeTruthy();
	});

	it('applies custom color when provided', () => {
		const { container } = render(Mono, { props: { color: '#c8412e' } });
		const span = container.querySelector('.mono-atom') as HTMLElement;
		expect(span.style.color).toBe('rgb(200, 65, 46)');
	});

	it('applies custom size when provided', () => {
		const { container } = render(Mono, { props: { size: 14 } });
		const span = container.querySelector('.mono-atom') as HTMLElement;
		expect(span.style.fontSize).toBe('14px');
	});
});

// ── Placeholder ──────────────────────────────────────────────────────────────

describe('Placeholder', () => {
	it('renders a span with aria-hidden', () => {
		const { container } = render(Placeholder, { props: {} });
		const el = container.querySelector('.placeholder');
		expect(el?.getAttribute('aria-hidden')).toBe('true');
	});

	it('applies default dimensions', () => {
		const { container } = render(Placeholder, { props: {} });
		const el = container.querySelector('.placeholder') as HTMLElement;
		expect(el.style.width).toBe('100%');
		expect(el.style.height).toBe('1em');
	});

	it('applies custom dimensions', () => {
		const { container } = render(Placeholder, { props: { width: '120px', height: '24px' } });
		const el = container.querySelector('.placeholder') as HTMLElement;
		expect(el.style.width).toBe('120px');
		expect(el.style.height).toBe('24px');
	});

	it('is block by default, inline when inline=true', () => {
		const { container } = render(Placeholder, { props: { inline: true } });
		const el = container.querySelector('.placeholder');
		expect(el?.classList.contains('inline')).toBe(true);
	});
});
