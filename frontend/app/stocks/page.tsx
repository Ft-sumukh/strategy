'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Building2, Search, ArrowRight, TrendingUp, ShieldCheck } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { SearchInput } from '../../components/ui/SearchInput';

const FLAGSHIP_COMPANIES = [
  {
    ticker: 'AAPL',
    name: 'Apple Inc.',
    exchange: 'NASDAQ',
    sector: 'Technology',
    industry: 'Consumer Electronics',
    marketCap: '$3,450.0B',
    price: '$226.55',
    change: '+0.85%',
    score: '88 / 100',
    grade: 'Exemplary',
  },
  {
    ticker: 'MSFT',
    name: 'Microsoft Corporation',
    exchange: 'NASDAQ',
    sector: 'Technology',
    industry: 'Software—Infrastructure',
    marketCap: '$3,200.0B',
    price: '$430.90',
    change: '+1.15%',
    score: '91 / 100',
    grade: 'Exemplary',
  },
  {
    ticker: 'NVDA',
    name: 'NVIDIA Corporation',
    exchange: 'NASDAQ',
    sector: 'Technology',
    industry: 'Semiconductors',
    marketCap: '$3,100.0B',
    price: '$126.45',
    change: '+3.40%',
    score: '94 / 100',
    grade: 'Exemplary',
  },
  {
    ticker: 'GOOG',
    name: 'Alphabet Inc.',
    exchange: 'NASDAQ',
    sector: 'Communication Services',
    industry: 'Internet Content & Information',
    marketCap: '$2,250.0B',
    price: '$182.28',
    change: '+0.45%',
    score: '86 / 100',
    grade: 'Exemplary',
  },
  {
    ticker: 'AMZN',
    name: 'Amazon.com Inc.',
    exchange: 'NASDAQ',
    sector: 'Consumer Cyclical',
    industry: 'Internet Retail',
    marketCap: '$1,980.0B',
    price: '$191.10',
    change: '+1.60%',
    score: '84 / 100',
    grade: 'Strong',
  },
];

export default function StocksPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = FLAGSHIP_COMPANIES.filter(
    (c) =>
      c.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.sector.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Flagship Equity Terminal"
        subtitle="Institutional research terminal covering financial statements, valuation, DCF models, technical indicators, and quantitative style factors."
        badge="PHASE 2 ENGINE ACTIVE"
      />

      <div className="max-w-md">
        <SearchInput
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Filter by ticker, company, or sector (e.g. NVDA, Apple, Consumer)..."
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((c) => (
          <Link
            key={c.ticker}
            href={`/stocks/${c.ticker}`}
            className="group block p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/60 shadow-lg hover:shadow-blue-500/10 transition-all duration-200 space-y-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-bold text-white font-mono group-hover:text-blue-400 transition-colors">
                    {c.ticker}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400">
                    {c.exchange}
                  </span>
                </div>
                <div className="text-sm font-medium text-slate-300 mt-0.5">{c.name}</div>
                <div className="text-xs text-slate-500">{c.industry}</div>
              </div>

              <div className="text-right font-mono">
                <div className="text-lg font-bold text-white">{c.price}</div>
                <div className="text-xs text-emerald-400 font-semibold">{c.change}</div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <div className="font-mono">
                <span className="text-slate-500 text-[10px] uppercase block">Market Cap</span>
                <span className="text-slate-200 font-bold">{c.marketCap}</span>
              </div>
              <div className="font-mono text-right">
                <span className="text-slate-500 text-[10px] uppercase block">Scorecard</span>
                <span className="text-blue-400 font-bold">{c.score}</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1 text-xs text-slate-400 group-hover:text-blue-400 font-medium">
              <span>Open Research Terminal</span>
              <ArrowRight className="h-4 w-4 transform group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
