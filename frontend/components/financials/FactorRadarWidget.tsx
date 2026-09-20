'use client';

import React from 'react';
import { FullFactors } from '../../lib/api/financials';
import { Target, HelpCircle, ShieldCheck } from 'lucide-react';

interface FactorRadarWidgetProps {
  factors: FullFactors;
}

export const FactorRadarWidget: React.FC<FactorRadarWidgetProps> = ({ factors }) => {
  const factorOrder = ['Momentum', 'Value', 'Quality', 'Size', 'Low Volatility', 'Growth', 'Liquidity'];

  const getExposureBadge = (exp: 'Strong' | 'Moderate' | 'Weak') => {
    if (exp === 'Strong') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
          STRONG
        </span>
      );
    }
    if (exp === 'Moderate') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-950 text-blue-300 border border-blue-800">
          MODERATE
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-800 text-slate-400 border border-slate-700">
        WEAK
      </span>
    );
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-cyan-400" />
            <h3 className="text-base font-semibold text-white">Quantitative Style Factor Exposures</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Normalized 7-factor institutional style profile, Z-scores, and cross-sectional percentile rankings
          </p>
        </div>

        <div className="px-3 py-1 bg-slate-950 rounded border border-slate-800 text-[11px] font-mono text-slate-300">
          UNIVERSE: US LARGE CAP
        </div>
      </div>

      {/* Factors List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {factorOrder.map((fName) => {
          const item = factors.factors[fName];
          if (!item) return null;

          const pct = item.percentile;
          const zScore = item.z_score;

          return (
            <div
              key={fName}
              className="p-3.5 bg-slate-950/60 rounded-lg border border-slate-800/80 hover:border-slate-700/80 transition-colors space-y-2.5"
            >
              {/* Title & Exposure */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-white">{fName}</span>
                  <span className="text-[10px] font-mono text-slate-400">
                    (Z: {zScore > 0 ? '+' : ''}
                    {zScore.toFixed(2)})
                  </span>
                </div>
                {getExposureBadge(item.exposure)}
              </div>

              {/* Percentile Bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-mono text-slate-400">
                  <span>Percentile Rank:</span>
                  <span className="text-slate-200 font-bold">{pct.toFixed(1)}%</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      pct >= 75 ? 'bg-cyan-500' : pct >= 40 ? 'bg-blue-500' : 'bg-slate-500'
                    }`}
                    style={{ width: `${Math.max(5, Math.min(100, pct))}%` }}
                  />
                </div>
              </div>

              {/* Description */}
              <p className="text-[11px] text-slate-400 leading-relaxed italic">{item.description}</p>
            </div>
          );
        })}
      </div>

      {/* Epistemic Notice */}
      <div className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-950/70 border border-slate-800/60 text-[11px] text-slate-400">
        <ShieldCheck className="h-4 w-4 text-slate-500 shrink-0" />
        <span>{factors.disclaimer}</span>
      </div>
    </div>
  );
};
