'use client';

import React, { useState } from 'react';
import { DCFModelResult, financialsApi } from '../../lib/api/financials';
import { Calculator, TrendingUp, TrendingDown, Sliders, RefreshCw, AlertCircle } from 'lucide-react';

interface DCFCalculatorWidgetProps {
  ticker: string;
  initialDCF: DCFModelResult;
}

export const DCFCalculatorWidget: React.FC<DCFCalculatorWidgetProps> = ({ ticker, initialDCF }) => {
  const [dcf, setDcf] = useState<DCFModelResult>(initialDCF);
  const [wacc, setWacc] = useState<number>(initialDCF.wacc);
  const [terminalGrowth, setTerminalGrowth] = useState<number>(initialDCF.terminal_growth_rate);
  const [growthStage1, setGrowthStage1] = useState<number>(initialDCF.stage1_growth_rate);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRecalculate = async () => {
    if (terminalGrowth >= wacc) {
      setErrorMsg('Terminal Growth Rate must be strictly less than WACC for Gordon Growth convergence.');
      return;
    }
    setErrorMsg(null);
    setIsLoading(true);
    try {
      const updated = await financialsApi.calculateDCF(ticker, {
        wacc,
        terminal_growth_rate: terminalGrowth,
        growth_rate_stage1: growthStage1,
      });
      setDcf(updated);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to recalculate DCF model.');
    } finally {
      setIsLoading(false);
    }
  };

  const isUpside = dcf.upside_downside_percent >= 0;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Calculator className="h-5 w-5 text-emerald-400" />
            <h3 className="text-base font-semibold text-white">Interactive DCF Valuation & Sensitivity Engine</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            5-Year Free Cash Flow to Firm (FCFF) Discounted Cash Flow Model with Gordon Growth Terminal Value
          </p>
        </div>

        {/* Intrinsic Price Card */}
        <div className="flex items-center gap-4 bg-slate-950 px-4 py-2.5 rounded-lg border border-slate-800">
          <div>
            <div className="text-[11px] text-slate-400 uppercase font-mono">Market vs Model Value</div>
            <div className="flex items-baseline gap-2">
              <span className="text-sm text-slate-400 font-mono">${dcf.current_price.toFixed(2)}</span>
              <span className="text-lg font-bold text-white font-mono">${dcf.implied_share_price.toFixed(2)}</span>
            </div>
          </div>
          <div
            className={`flex items-center gap-1 px-2.5 py-1 rounded text-xs font-mono font-bold ${
              isUpside ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'
            }`}
          >
            {isUpside ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
            {isUpside ? '+' : ''}
            {dcf.upside_downside_percent.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Assumption Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 p-4 bg-slate-950/70 border border-slate-800/80 rounded-lg">
        {/* WACC */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-300">Discount Rate (WACC)</span>
            <span className="text-blue-400 font-bold">{(wacc * 100).toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="0.05"
            max="0.18"
            step="0.005"
            value={wacc}
            onChange={(e) => setWacc(parseFloat(e.target.value))}
            className="w-full accent-blue-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>5.0%</span>
            <span>18.0%</span>
          </div>
        </div>

        {/* 5-Yr Growth */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-300">5-Year FCF Growth Rate</span>
            <span className="text-emerald-400 font-bold">{(growthStage1 * 100).toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="-0.10"
            max="0.30"
            step="0.01"
            value={growthStage1}
            onChange={(e) => setGrowthStage1(parseFloat(e.target.value))}
            className="w-full accent-emerald-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-10.0%</span>
            <span>+30.0%</span>
          </div>
        </div>

        {/* Terminal Growth */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-300">Terminal Growth Rate</span>
            <span className="text-amber-400 font-bold">{(terminalGrowth * 100).toFixed(2)}%</span>
          </div>
          <input
            type="range"
            min="0.01"
            max="0.05"
            step="0.0025"
            value={terminalGrowth}
            onChange={(e) => setTerminalGrowth(parseFloat(e.target.value))}
            className="w-full accent-amber-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>1.0%</span>
            <span>5.0%</span>
          </div>
        </div>
      </div>

      {/* Recalculate Button */}
      <div className="flex items-center justify-between">
        <button
          onClick={handleRecalculate}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow-sm transition-all"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          Recalculate Valuation Model
        </button>

        {errorMsg && (
          <div className="flex items-center gap-1.5 text-xs text-rose-400 font-medium">
            <AlertCircle className="h-4 w-4" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* 5-Year Projection Breakdown */}
      <div className="overflow-x-auto">
        <div className="text-xs font-semibold text-slate-300 mb-2 font-sans">
          5-Year Projected Free Cash Flows (Base FCF: ${(dcf.fcf_base / 1_000_000_000).toFixed(2)}B)
        </div>
        <table className="w-full text-left text-xs font-mono text-slate-300">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2 px-3">Metric</th>
              {dcf.projections.map((p) => (
                <th key={p.year} className="py-2 px-3 text-right">
                  Year {p.year}
                </th>
              ))}
              <th className="py-2 px-3 text-right text-amber-400">Terminal Value</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            <tr>
              <td className="py-2 px-3 font-sans text-slate-400">Projected FCF</td>
              {dcf.projections.map((p) => (
                <td key={p.year} className="py-2 px-3 text-right">
                  ${(p.projected_fcf / 1_000_000_000).toFixed(2)}B
                </td>
              ))}
              <td className="py-2 px-3 text-right text-amber-300 font-semibold">
                ${(dcf.terminal_value / 1_000_000_000).toFixed(2)}B
              </td>
            </tr>
            <tr>
              <td className="py-2 px-3 font-sans text-slate-400">Discount Factor</td>
              {dcf.projections.map((p) => (
                <td key={p.year} className="py-2 px-3 text-right text-slate-500">
                  {p.discount_factor.toFixed(4)}
                </td>
              ))}
              <td className="py-2 px-3 text-right text-slate-500">
                {(1.0 / (1.0 + dcf.wacc) ** 5).toFixed(4)}
              </td>
            </tr>
            <tr className="font-semibold text-emerald-400 bg-slate-950/40">
              <td className="py-2 px-3 font-sans text-slate-200">Present Value (PV)</td>
              {dcf.projections.map((p) => (
                <td key={p.year} className="py-2 px-3 text-right">
                  ${(p.pv_fcf / 1_000_000_000).toFixed(2)}B
                </td>
              ))}
              <td className="py-2 px-3 text-right text-emerald-300 font-bold">
                ${(dcf.pv_terminal_value / 1_000_000_000).toFixed(2)}B
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* 2D Sensitivity Matrix */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="text-xs font-semibold text-slate-200 font-sans">
            2D Sensitivity Matrix: Implied Share Price by WACC &times; Terminal Growth
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Cell: Share Price (Upside %)</span>
        </div>

        <div className="overflow-x-auto border border-slate-800 rounded-lg">
          <table className="w-full text-center text-xs font-mono">
            <thead>
              <tr className="bg-slate-950 border-b border-slate-800 text-slate-400">
                <th className="py-2 px-3 text-left font-sans">WACC \ Term Growth</th>
                {dcf.sensitivity_growth_labels.map((g) => (
                  <th key={g} className="py-2 px-3">
                    {(g * 100).toFixed(2)}%
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {dcf.sensitivity_matrix.map((row, rIdx) => {
                const rowWacc = dcf.sensitivity_wacc_labels[rIdx];
                return (
                  <tr key={rowWacc} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2 px-3 text-left font-bold text-slate-300 bg-slate-950/50">
                      {(rowWacc * 100).toFixed(1)}%
                    </td>
                    {row.map((cell, cIdx) => {
                      const isBase =
                        Math.abs(cell.wacc - dcf.wacc) < 0.001 &&
                        Math.abs(cell.terminal_growth - dcf.terminal_growth_rate) < 0.001;
                      const cellUpside = cell.upside_percent >= 0;

                      return (
                        <td
                          key={cIdx}
                          className={`py-2 px-3 transition-all ${
                            isBase ? 'bg-blue-600/30 border-2 border-blue-400 font-bold' : ''
                          }`}
                        >
                          <div className="text-slate-100 font-semibold">${cell.implied_share_price.toFixed(2)}</div>
                          <div
                            className={`text-[10px] ${
                              cellUpside ? 'text-emerald-400' : 'text-rose-400'
                            }`}
                          >
                            {cellUpside ? '+' : ''}
                            {cell.upside_percent.toFixed(1)}%
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Disclaimer */}
      <p className="text-[11px] text-slate-500 leading-relaxed italic border-t border-slate-800 pt-3">
        {dcf.disclaimer}
      </p>
    </div>
  );
};
