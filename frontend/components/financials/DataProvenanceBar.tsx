'use client';

import React from 'react';
import { Database, ShieldCheck, Info, Calendar, DollarSign } from 'lucide-react';

interface DataProvenanceBarProps {
  dataSource?: string;
  asOfDate?: string;
  currency?: string;
  qualityStatus?: string;
  isSynthetic?: boolean;
}

export const DataProvenanceBar: React.FC<DataProvenanceBarProps> = ({
  dataSource = 'SEC_EDGAR_DEMO',
  asOfDate = '2025 / TTM',
  currency = 'USD',
  qualityStatus = 'AUDITED',
  isSynthetic = true,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 bg-slate-900/90 border border-slate-800 rounded-lg text-xs text-slate-300">
      <div className="flex flex-wrap items-center gap-4">
        {/* Source */}
        <div className="flex items-center gap-1.5 font-mono text-slate-400">
          <Database className="h-3.5 w-3.5 text-blue-400" />
          <span>PROVENANCE:</span>
          <span className="text-slate-200 font-semibold">{dataSource}</span>
        </div>

        {/* As of Date */}
        <div className="flex items-center gap-1.5 font-mono text-slate-400">
          <Calendar className="h-3.5 w-3.5 text-slate-400" />
          <span>AS-OF:</span>
          <span className="text-slate-200">{asOfDate}</span>
        </div>

        {/* Currency */}
        <div className="flex items-center gap-1 font-mono text-slate-400">
          <DollarSign className="h-3.5 w-3.5 text-emerald-400" />
          <span>CURRENCY:</span>
          <span className="text-emerald-400 font-semibold">{currency}</span>
        </div>

        {/* Quality status */}
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span className="px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 font-mono text-[11px] font-semibold">
            {qualityStatus}
          </span>
        </div>
      </div>

      {/* Synthetic / Demo Disclosure */}
      <div className="flex items-center gap-1.5 text-amber-300/90 font-medium">
        <Info className="h-3.5 w-3.5 text-amber-400" />
        <span>{isSynthetic ? 'Sandbox / Historical Demo Telemetry (SEC Audited Figures)' : 'Production Live Telemetry'}</span>
      </div>
    </div>
  );
};
