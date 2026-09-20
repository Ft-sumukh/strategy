'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  financialsApi,
  ScreenerStockItem,
  ScreenerResponse,
} from '../../lib/api/financials';
import { ComparisonModal } from '../../components/financials/ComparisonModal';
import { PageHeader } from '../../components/ui/PageHeader';
import {
  Filter,
  SlidersHorizontal,
  Scale,
  ArrowUpDown,
  ExternalLink,
  RefreshCw,
  Search,
  CheckSquare,
  Square,
} from 'lucide-react';

export default function ScreenerPage() {
  const [items, setItems] = useState<ScreenerStockItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [sector, setSector] = useState<string>('');
  const [minScorecard, setMinScorecard] = useState<number | undefined>(undefined);
  const [maxPe, setMaxPe] = useState<number | undefined>(undefined);
  const [minFcfYield, setMinFcfYield] = useState<number | undefined>(undefined);
  const [sortBy, setSortBy] = useState<string>('market_cap');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Comparison selection
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState<boolean>(false);

  const fetchScreener = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await financialsApi.runScreener({
        sector: sector || undefined,
        min_scorecard: minScorecard,
        max_pe: maxPe,
        min_fcf_yield: minFcfYield,
        sort_by: sortBy,
        sort_direction: sortDirection,
        page: 1,
        limit: 50,
      });
      setItems(res.items);
      setTotal(res.total);
    } catch (err: any) {
      setError(err.message || 'Failed to execute screener query.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScreener();
  }, [sector, minScorecard, maxPe, minFcfYield, sortBy, sortDirection]);

  const toggleSelectStock = (ticker: string) => {
    setSelectedTickers((prev) => {
      if (prev.includes(ticker)) {
        return prev.filter((t) => t !== ticker);
      }
      if (prev.length >= 4) {
        alert('You can select a maximum of 4 stocks for side-by-side comparison.');
        return prev;
      }
      return [...prev, ticker];
    });
  };

  const selectedStocks = items.filter((s) => selectedTickers.includes(s.ticker));

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortDirection((prev) => (prev === 'desc' ? 'asc' : 'desc'));
    } else {
      setSortBy(field);
      setSortDirection('desc');
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Multi-Factor Equity Screener"
        subtitle="Institutional multi-factor asset screening with safe SQL parameterization, financial ratio filters, and comparative side-by-side mode."
        badge="PHASE 2 ENGINE ACTIVE"
      />

      {/* Filter Controls Bar */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl shadow-lg space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Sector Filter */}
            <div>
              <label className="block text-[10px] uppercase font-mono text-slate-400 mb-1">Sector</label>
              <select
                value={sector}
                onChange={(e) => setSector(e.target.value)}
                className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-sans focus:outline-none focus:border-blue-500"
              >
                <option value="">All Sectors</option>
                <option value="Technology">Technology</option>
                <option value="Communication Services">Communication Services</option>
                <option value="Consumer Cyclical">Consumer Cyclical</option>
              </select>
            </div>

            {/* Scorecard Filter */}
            <div>
              <label className="block text-[10px] uppercase font-mono text-slate-400 mb-1">Min Scorecard</label>
              <select
                value={minScorecard !== undefined ? String(minScorecard) : ''}
                onChange={(e) => setMinScorecard(e.target.value ? Number(e.target.value) : undefined)}
                className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500"
              >
                <option value="">Any Score</option>
                <option value="70">&ge; 70 (Strong)</option>
                <option value="80">&ge; 80 (Exemplary)</option>
                <option value="90">&ge; 90 (Elite)</option>
              </select>
            </div>

            {/* Max P/E Filter */}
            <div>
              <label className="block text-[10px] uppercase font-mono text-slate-400 mb-1">Max P/E Ratio</label>
              <select
                value={maxPe !== undefined ? String(maxPe) : ''}
                onChange={(e) => setMaxPe(e.target.value ? Number(e.target.value) : undefined)}
                className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500"
              >
                <option value="">Any Valuation</option>
                <option value="40">&le; 40x</option>
                <option value="35">&le; 35x</option>
                <option value="30">&le; 30x</option>
              </select>
            </div>

            {/* Min FCF Yield Filter */}
            <div>
              <label className="block text-[10px] uppercase font-mono text-slate-400 mb-1">Min FCF Yield</label>
              <select
                value={minFcfYield !== undefined ? String(minFcfYield) : ''}
                onChange={(e) => setMinFcfYield(e.target.value ? Number(e.target.value) : undefined)}
                className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500"
              >
                <option value="">Any Yield</option>
                <option value="0.02">&ge; 2.0%</option>
                <option value="0.03">&ge; 3.0%</option>
                <option value="0.04">&ge; 4.0%</option>
              </select>
            </div>
          </div>

          {/* Action: Compare Modal Trigger */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsCompareModalOpen(true)}
              disabled={selectedTickers.length < 2}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold shadow-sm transition-all ${
                selectedTickers.length >= 2
                  ? 'bg-blue-600 hover:bg-blue-500 text-white cursor-pointer'
                  : 'bg-slate-800 text-slate-500 cursor-not-allowed opacity-60'
              }`}
            >
              <Scale className="h-4 w-4" />
              Compare Mode ({selectedTickers.length})
            </button>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-lg overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>MATCHING SECURITIES: {total}</span>
          <span>Click column header to sort &bull; Select 2–4 checkboxes to compare</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs font-mono">
            <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2 text-blue-500" />
            Evaluating screening constraints...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400 text-xs font-mono">{error}</div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs font-mono">
            No assets match the active filter criteria. Try adjusting constraints.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/60">
                  <th className="py-3 px-4 w-10 text-center">
                    <span className="sr-only">Select</span>
                  </th>
                  <th
                    onClick={() => handleSort('ticker')}
                    className="py-3 px-4 cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center gap-1">
                      Ticker <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4 font-sans">Company</th>
                  <th className="py-3 px-4 font-sans">Sector</th>
                  <th
                    onClick={() => handleSort('market_cap')}
                    className="py-3 px-4 text-right cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-end gap-1">
                      Market Cap <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4 text-right">Price</th>
                  <th
                    onClick={() => handleSort('pe_ratio')}
                    className="py-3 px-4 text-right cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-end gap-1">
                      P/E <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('fcf_yield')}
                    className="py-3 px-4 text-right cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-end gap-1">
                      FCF Yield <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4 text-right">3Y CAGR</th>
                  <th
                    onClick={() => handleSort('scorecard_score')}
                    className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-center gap-1">
                      Scorecard <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </th>
                  <th className="py-3 px-4 text-center">Technical Bias</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {items.map((stock) => {
                  const isChecked = selectedTickers.includes(stock.ticker);
                  return (
                    <tr
                      key={stock.ticker}
                      className={`hover:bg-slate-800/40 transition-colors ${
                        isChecked ? 'bg-blue-950/20' : ''
                      }`}
                    >
                      {/* Checkbox */}
                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => toggleSelectStock(stock.ticker)}
                          className="text-slate-400 hover:text-blue-400 transition-colors"
                        >
                          {isChecked ? (
                            <CheckSquare className="h-4 w-4 text-blue-500" />
                          ) : (
                            <Square className="h-4 w-4" />
                          )}
                        </button>
                      </td>

                      {/* Ticker Link */}
                      <td className="py-3 px-4">
                        <Link
                          href={`/stocks/${stock.ticker}`}
                          className="font-bold text-blue-400 hover:text-blue-300 inline-flex items-center gap-1 group"
                        >
                          {stock.ticker}
                          <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </Link>
                      </td>

                      <td className="py-3 px-4 font-sans text-slate-300 font-medium">{stock.name}</td>
                      <td className="py-3 px-4 font-sans text-slate-400">{stock.sector}</td>

                      <td className="py-3 px-4 text-right text-slate-100 font-bold">
                        ${(stock.market_cap / 1_000_000_000).toFixed(1)}B
                      </td>
                      <td className="py-3 px-4 text-right text-slate-200">${stock.price.toFixed(2)}</td>

                      <td className="py-3 px-4 text-right text-slate-300">
                        {stock.pe_ratio ? `${stock.pe_ratio.toFixed(1)}x` : '—'}
                      </td>

                      <td className="py-3 px-4 text-right text-emerald-400 font-semibold">
                        {stock.fcf_yield ? `${(stock.fcf_yield * 100).toFixed(1)}%` : '—'}
                      </td>

                      <td className="py-3 px-4 text-right text-slate-300">
                        {stock.revenue_cagr_3y ? `${(stock.revenue_cagr_3y * 100).toFixed(1)}%` : '—'}
                      </td>

                      <td className="py-3 px-4 text-center">
                        <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold text-[11px]">
                          {stock.scorecard_score ? Math.round(stock.scorecard_score) : '—'} / 100
                        </span>
                      </td>

                      <td className="py-3 px-4 text-center">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            stock.overall_sentiment === 'BULLISH'
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                              : stock.overall_sentiment === 'BEARISH'
                              ? 'bg-rose-950 text-rose-300 border border-rose-800'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {stock.overall_sentiment}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Side-by-Side Comparison Modal */}
      <ComparisonModal
        isOpen={isCompareModalOpen}
        onClose={() => setIsCompareModalOpen(false)}
        selectedStocks={selectedStocks}
      />
    </div>
  );
}
