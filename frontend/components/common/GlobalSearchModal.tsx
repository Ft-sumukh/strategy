'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Search, X, Layers, Briefcase, FileText, Newspaper, GitBranch, ArrowUpRight } from 'lucide-react';
import { GlobalSearchItem } from '../../lib/types';
import { cn } from '../../lib/utils';

interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SAMPLE_SEARCH_ITEMS: GlobalSearchItem[] = [
  { id: '1', title: 'NVDA — NVIDIA Corp.', subtitle: 'NASDAQ • Semiconductor • Tech', category: 'Stocks', url: '/stocks', badge: 'Active' },
  { id: '2', title: 'AAPL — Apple Inc.', subtitle: 'NASDAQ • Consumer Electronics', category: 'Stocks', url: '/stocks', badge: 'Active' },
  { id: '3', title: 'MSFT — Microsoft Corp.', subtitle: 'NASDAQ • Systems Software', category: 'Stocks', url: '/stocks', badge: 'Active' },
  { id: '4', title: 'Core Multi-Factor Equity', subtitle: 'Quant Strategy • Momentum + Quality', category: 'Strategies', url: '/strategies', badge: 'Model' },
  { id: '5', title: 'Macro Regime Transition Alpha', subtitle: 'Macro Strategy • Rate Cycle', category: 'Strategies', url: '/strategies', badge: 'Model' },
  { id: '6', title: 'Flagship Growth Portfolio', subtitle: 'US Equities • $10,000,000 AUM', category: 'Portfolios', url: '/portfolio', badge: 'USD' },
  { id: '7', title: 'Semiconductor Capital Cycle Analysis', subtitle: 'AI Research Synthesis • H2 2026', category: 'Research', url: '/research', badge: 'AI Report' },
  { id: '8', title: 'Federal Reserve Policy Shift & Yield Curves', subtitle: 'Macro Research • Inversion Dynamics', category: 'News', url: '/news', badge: 'Macro' },
];

const CATEGORIES: ('All' | GlobalSearchItem['category'])[] = [
  'All',
  'Stocks',
  'Companies',
  'Strategies',
  'Portfolios',
  'Research',
  'News',
];

export function GlobalSearchModal({ isOpen, onClose }: GlobalSearchModalProps) {
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'All' | GlobalSearchItem['category']>('All');

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const filteredItems = useMemo(() => {
    return SAMPLE_SEARCH_ITEMS.filter((item) => {
      const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
      const matchesQuery =
        query.trim() === '' ||
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.subtitle.toLowerCase().includes(query.toLowerCase());
      return matchesCategory && matchesQuery;
    });
  }, [query, selectedCategory]);

  if (!isOpen) return null;

  const getCategoryIcon = (category: GlobalSearchItem['category']) => {
    switch (category) {
      case 'Stocks':
      case 'Companies':
        return <Layers className="h-4 w-4 text-blue-400" />;
      case 'Strategies':
        return <GitBranch className="h-4 w-4 text-purple-400" />;
      case 'Portfolios':
        return <Briefcase className="h-4 w-4 text-emerald-400" />;
      case 'Research':
        return <FileText className="h-4 w-4 text-amber-400" />;
      case 'News':
        return <Newspaper className="h-4 w-4 text-cyan-400" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl rounded-xl border border-border bg-[#0B0F19] shadow-2xl overflow-hidden">
        {/* Search Header */}
        <div className="flex items-center px-4 py-3 border-b border-border/80 gap-3">
          <Search className="h-5 w-5 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search stocks, companies, strategies, portfolios, research, news..."
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
            autoFocus
          />
          {query && (
            <button onClick={() => setQuery('')} className="p-1 text-slate-500 hover:text-slate-300">
              <X className="h-4 w-4" />
            </button>
          )}
          <button
            onClick={onClose}
            className="rounded border border-border px-1.5 py-0.5 text-[10px] font-mono text-slate-400 hover:bg-slate-800"
          >
            ESC
          </button>
        </div>

        {/* Category Filters */}
        <div className="flex items-center gap-1 px-4 py-2 bg-slate-900/50 border-b border-border/60 overflow-x-auto">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                'px-2.5 py-1 rounded-md text-xs font-medium transition-colors whitespace-nowrap',
                selectedCategory === cat
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              )}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search Results */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredItems.length > 0 ? (
            filteredItems.map((item) => (
              <a
                key={item.id}
                href={item.url}
                onClick={onClose}
                className="flex items-center justify-between p-2.5 rounded-lg hover:bg-slate-800/60 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-md bg-slate-800/80 border border-border/50">
                    {getCategoryIcon(item.category)}
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 flex items-center gap-2">
                      <span>{item.title}</span>
                      {item.badge && (
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-border">
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-slate-400">{item.subtitle}</div>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-500 group-hover:text-slate-300">
                  <span className="text-[10px] font-mono uppercase">{item.category}</span>
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </div>
              </a>
            ))
          ) : (
            <div className="py-8 text-center text-xs text-slate-500">
              No matching records found for "{query}".
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-border/60 bg-slate-950/60 text-[11px] text-slate-500 flex justify-between">
          <span>Global Search UI Foundation</span>
          <span className="font-mono">Navigation Ready</span>
        </div>
      </div>
    </div>
  );
}
