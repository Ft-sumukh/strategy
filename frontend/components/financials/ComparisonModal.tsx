'use client';

import React from 'react';
import { ScreenerStockItem } from '../../lib/api/financials';
import { X, Scale, ExternalLink } from 'lucide-react';
import Link from 'next/link';

interface ComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedStocks: ScreenerStockItem[];
}

export const ComparisonModal: React.FC<ComparisonModalProps> = ({
  isOpen,
  onClose,
  selectedStocks,
}) => {
  if (!isOpen || selectedStocks.length === 0) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-2">
            <Scale className="h-5 w-5 text-blue-400" />
            <h3 className="text-base font-semibold text-white">Side-by-Side Asset Comparison</h3>
            <span className="text-xs text-slate-400">({selectedStocks.length} Selected)</span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body: Comparison Table */}
        <div className="overflow-y-auto p-6 space-y-6">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono">
                <th className="py-3 px-4 font-sans text-slate-300 w-1/4">Metric</th>
                {selectedStocks.map((s) => (
                  <th key={s.ticker} className="py-3 px-4 text-center">
                    <div className="flex flex-col items-center gap-1">
                      <Link
                        href={`/stocks/${s.ticker}`}
                        className="text-sm font-bold text-blue-400 hover:text-blue-300 inline-flex items-center gap-1 font-mono"
                      >
                        {s.ticker} <ExternalLink className="h-3 w-3" />
                      </Link>
                      <span className="text-[11px] font-sans text-slate-300 font-normal truncate max-w-[140px]">
                        {s.name}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {/* Profile */}
              <tr className="bg-slate-950/40">
                <td colSpan={selectedStocks.length + 1} className="py-2 px-4 font-sans text-[11px] font-semibold text-blue-400 uppercase tracking-wider">
                  Company Profile
                </td>
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Sector</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-200">
                    {s.sector}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Market Cap</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-100 font-bold">
                    ${(s.market_cap / 1_000_000_000).toFixed(1)}B
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Current Price</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-200">
                    ${s.price.toFixed(2)}
                  </td>
                ))}
              </tr>

              {/* Valuation Multiples */}
              <tr className="bg-slate-950/40">
                <td colSpan={selectedStocks.length + 1} className="py-2 px-4 font-sans text-[11px] font-semibold text-blue-400 uppercase tracking-wider">
                  Valuation Multiples
                </td>
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">P/E Ratio</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-200">
                    {s.pe_ratio ? `${s.pe_ratio.toFixed(1)}x` : '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">EV / EBITDA</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-200">
                    {s.ev_to_ebitda ? `${s.ev_to_ebitda.toFixed(1)}x` : '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">FCF Yield</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-emerald-400 font-semibold">
                    {s.fcf_yield ? `${(s.fcf_yield * 100).toFixed(1)}%` : '—'}
                  </td>
                ))}
              </tr>

              {/* Fundamentals & Scorecard */}
              <tr className="bg-slate-950/40">
                <td colSpan={selectedStocks.length + 1} className="py-2 px-4 font-sans text-[11px] font-semibold text-blue-400 uppercase tracking-wider">
                  Fundamentals & Scorecard
                </td>
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">3Y Revenue CAGR</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-200">
                    {s.revenue_cagr_3y ? `${(s.revenue_cagr_3y * 100).toFixed(1)}%` : '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Return on Equity (ROE)</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-200">
                    {s.roe ? `${(s.roe * 100).toFixed(1)}%` : '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Fundamental Scorecard</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center font-bold text-white">
                    <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                      {s.scorecard_score ? Math.round(s.scorecard_score) : '—'} / 100
                    </span>
                  </td>
                ))}
              </tr>

              {/* Technicals & Factors */}
              <tr className="bg-slate-950/40">
                <td colSpan={selectedStocks.length + 1} className="py-2 px-4 font-sans text-[11px] font-semibold text-blue-400 uppercase tracking-wider">
                  Technicals & Style Factors
                </td>
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Technical Sentiment</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        s.overall_sentiment === 'BULLISH'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : s.overall_sentiment === 'BEARISH'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {s.overall_sentiment}
                    </span>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">RSI (14)</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-slate-200">
                    {s.rsi_14?.toFixed(1) ?? '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Momentum Factor (Percentile)</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-cyan-400 font-semibold">
                    {s.momentum_factor ? `${s.momentum_factor.toFixed(0)}%` : '—'}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-4 text-slate-400 font-sans">Quality Factor (Percentile)</td>
                {selectedStocks.map((s) => (
                  <td key={s.ticker} className="py-2.5 px-4 text-center text-purple-400 font-semibold">
                    {s.quality_factor ? `${s.quality_factor.toFixed(0)}%` : '—'}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between text-xs text-slate-400">
          <span>
            Comparison does not declare artificial "winners" or generate automated buy/sell recommendations.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
