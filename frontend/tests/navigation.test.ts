/**
 * Tests for Frontend Navigation, Routes, and Shell Structure
 */

import { describe, it, expect } from 'vitest';
import { NAV_ITEMS } from '../components/navigation/Sidebar';

describe('Navigation Shell & Planned Routes', () => {
  it('contains exactly the 18 planned route navigation items', () => {
    expect(NAV_ITEMS).toHaveLength(18);

    const routeNames = NAV_ITEMS.map((item) => item.name);
    expect(routeNames).toEqual([
      'Overview',
      'Markets',
      'Screener',
      'Stocks',
      'Research',
      'News',
      'Macro',
      'Strategies',
      'Backtesting',
      'Risk',
      'Stress Test',
      'Portfolio',
      'Watchlist',
      'Alerts',
      'AI Research',
      'Experiments',
      'Models',
      'Settings',
    ]);
  });

  it('maps each navigation item to its unique valid route path', () => {
    const paths = NAV_ITEMS.map((item) => item.href);
    const uniquePaths = new Set(paths);
    expect(uniquePaths.size).toBe(18);

    expect(paths).toContain('/dashboard');
    expect(paths).toContain('/markets');
    expect(paths).toContain('/screener');
    expect(paths).toContain('/stocks');
    expect(paths).toContain('/research');
    expect(paths).toContain('/news');
    expect(paths).toContain('/macro');
    expect(paths).toContain('/strategies');
    expect(paths).toContain('/backtesting');
    expect(paths).toContain('/risk');
    expect(paths).toContain('/stress-test');
    expect(paths).toContain('/portfolio');
    expect(paths).toContain('/watchlist');
    expect(paths).toContain('/alerts');
    expect(paths).toContain('/ai-research');
    expect(paths).toContain('/experiments');
    expect(paths).toContain('/models');
    expect(paths).toContain('/settings');
  });

  it('equips each item with an icon component', () => {
    for (const item of NAV_ITEMS) {
      expect(item.icon).toBeDefined();
      expect(typeof item.icon).toBe('object'); // Lucide forwardRef icon object
    }
  });
});
