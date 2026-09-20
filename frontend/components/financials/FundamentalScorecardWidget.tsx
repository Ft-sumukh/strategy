'use client';

import React from 'react';
import { FundamentalScorecard } from '../../lib/api/financials';
import { Award, CheckCircle2, AlertTriangle, ShieldCheck, ChevronDown } from 'lucide-react';

interface FundamentalScorecardWidgetProps {
  scorecard: FundamentalScorecard;
}

export const FundamentalScorecardWidget: React.FC<FundamentalScorecardWidgetProps> = ({ scorecard }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/50 bg-emerald-950/40';
    if (score >= 65) return 'text-blue-400 border-blue-500/50 bg-blue-950/40';
    if (score >= 50) return 'text-amber-400 border-amber-500/50 bg-amber-950/40';
    return 'text-rose-400 border-rose-500/50 bg-rose-950/40';
  };

  const getStatusBadge = (status: string) => {
    if (status === 'Strong') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950/80 text-emerald-300 border border-emerald-800">
          <CheckCircle2 className="h-3 w-3" /> Strong
        </span>
      );
    }
    if (status === 'Adequate') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-950/80 text-blue-300 border border-blue-800">
          Adequate
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-950/80 text-rose-300 border border-rose-800">
        <AlertTriangle className="h-3 w-3" /> Weak
      </span>
    );
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-5">
      {/* Header & Overall Score */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Award className="h-5 w-5 text-amber-400" />
            <h3 className="text-base font-semibold text-white">Institutional Fundamental Scorecard</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Transparent 6-pillar deterministic quantitative assessment (as-of {scorecard.as_of_period})
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-mono">Overall Score</div>
            <div className="text-xs font-semibold text-slate-300">{scorecard.rating} Grade</div>
          </div>
          <div
            className={`flex items-center justify-center h-14 w-14 rounded-xl border-2 font-mono text-2xl font-bold ${getScoreColor(
              scorecard.overall_score
            )}`}
          >
            {Math.round(scorecard.overall_score)}
          </div>
        </div>
      </div>

      {/* 6 Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {scorecard.categories.map((cat) => (
          <div
            key={cat.name}
            className="p-3.5 rounded-lg bg-slate-950/50 border border-slate-800/80 hover:border-slate-700/80 transition-colors space-y-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200">{cat.name}</span>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono text-slate-400">{(cat.weight * 100).toFixed(0)}% Wgt</span>
                {getStatusBadge(cat.status)}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-[11px] font-mono text-slate-400">
                <span>Score: {Math.round(cat.score)} / 100</span>
                <span>Contribution: +{cat.weighted_score.toFixed(1)} pts</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    cat.score >= 70 ? 'bg-emerald-500' : cat.score >= 45 ? 'bg-blue-500' : 'bg-rose-500'
                  }`}
                  style={{ width: `${Math.max(5, Math.min(100, cat.score))}%` }}
                />
              </div>
            </div>

            {/* Rationale */}
            <p className="text-[11px] text-slate-400 leading-relaxed italic">{cat.rationale}</p>
          </div>
        ))}
      </div>

      {/* Epistemic Disclaimer */}
      <div className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-950/70 border border-slate-800/60 text-[11px] text-slate-400">
        <ShieldCheck className="h-4 w-4 text-slate-500 shrink-0" />
        <span>
          {scorecard.disclaimer ||
            'Scorecard is a deterministic quantitative aggregation across 6 fundamental pillars. It does not constitute investment advice or a price forecast.'}
        </span>
      </div>
    </div>
  );
};
