import { describe, it, expect } from 'vitest';
import {
	GROUP_COLORS,
	SPECTRUM,
	getVoteColorVar,
	normalizePosition,
	sortBySpectrum,
	getGroupColor,
} from './tokens';

describe('tokens', () => {
	describe('GROUP_COLORS', () => {
		it('covers all spectrum groups', () => {
			for (const acro of SPECTRUM) {
				expect(GROUP_COLORS[acro]).toBeDefined();
				expect(GROUP_COLORS[acro]).toMatch(/^#[0-9a-f]{6}$/i);
			}
		});

		it('uses identical color for synonym pairs (LFI/LFI-NFP, RE/EPR, LR/DR)', () => {
			expect(GROUP_COLORS.LFI).toBe(GROUP_COLORS['LFI-NFP']);
			expect(GROUP_COLORS.RE).toBe(GROUP_COLORS.EPR);
			expect(GROUP_COLORS.LR).toBe(GROUP_COLORS.DR);
			expect(GROUP_COLORS.PCF).toBe(GROUP_COLORS.GDR);
		});
	});

	describe('getVoteColorVar', () => {
		it('maps each position to its CSS variable', () => {
			expect(getVoteColorVar('pour')).toBe('--pour');
			expect(getVoteColorVar('contre')).toBe('--contre');
			expect(getVoteColorVar('abst')).toBe('--abst');
			expect(getVoteColorVar('absent')).toBe('--absent');
		});
	});

	describe('normalizePosition', () => {
		it('returns canonical forms unchanged', () => {
			expect(normalizePosition('pour')).toBe('pour');
			expect(normalizePosition('contre')).toBe('contre');
			expect(normalizePosition('abst')).toBe('abst');
			expect(normalizePosition('absent')).toBe('absent');
		});

		it('normalizes uppercase and variants', () => {
			expect(normalizePosition('POUR')).toBe('pour');
			expect(normalizePosition('Contre')).toBe('contre');
			expect(normalizePosition('abstention')).toBe('abst');
			expect(normalizePosition('Abstention')).toBe('abst');
		});

		it('maps English synonyms', () => {
			expect(normalizePosition('for')).toBe('pour');
			expect(normalizePosition('against')).toBe('contre');
		});

		it('defaults to absent for unknown values', () => {
			expect(normalizePosition('non_votant')).toBe('absent');
			expect(normalizePosition('')).toBe('absent');
			expect(normalizePosition('unknown')).toBe('absent');
		});
	});

	describe('sortBySpectrum', () => {
		it('orders groups left to right', () => {
			const input = [
				{ acronyme: 'RN' },
				{ acronyme: 'LFI' },
				{ acronyme: 'DEM' },
				{ acronyme: 'NI' },
			];
			const sorted = sortBySpectrum(input);
			expect(sorted.map((g) => g.acronyme)).toEqual(['LFI', 'DEM', 'RN', 'NI']);
		});

		it('places synonyms at the same spectrum position as their canonical form', () => {
			const input = [
				{ acronyme: 'DR' },      // = LR position
				{ acronyme: 'LFI-NFP' }, // = LFI position
				{ acronyme: 'EPR' },     // = RE position
			];
			const sorted = sortBySpectrum(input);
			expect(sorted.map((g) => g.acronyme)).toEqual(['LFI-NFP', 'EPR', 'DR']);
		});

		it('places unknown acronyms at the end', () => {
			const input = [
				{ acronyme: 'MYSTERY' },
				{ acronyme: 'LFI' },
				{ acronyme: 'RN' },
			];
			const sorted = sortBySpectrum(input);
			expect(sorted[0].acronyme).toBe('LFI');
			expect(sorted[sorted.length - 1].acronyme).toBe('MYSTERY');
		});

		it('does not mutate the input array', () => {
			const input = [{ acronyme: 'RN' }, { acronyme: 'LFI' }];
			const original = [...input];
			sortBySpectrum(input);
			expect(input).toEqual(original);
		});
	});

	describe('getGroupColor', () => {
		it('returns the configured color for known groups', () => {
			expect(getGroupColor('LFI')).toBe('#c12c44');
			expect(getGroupColor('RN')).toBe('#0d2f6e');
		});

		it('returns the neutral grey fallback for unknown groups', () => {
			expect(getGroupColor('MYSTERY')).toBe('#888888');
		});
	});
});
