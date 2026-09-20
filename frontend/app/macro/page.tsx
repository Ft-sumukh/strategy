'use client';

import React from 'react';
import { Globe, TrendingDown, Percent, Landmark } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Card, CardContent } from '../../components/ui/Card';

export default function MacroPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Macroeconomic Conditions & Regimes"
        subtitle="Monetary policy indicators, inflation metrics, yield curve inversion dynamics, and business cycle regimes."
        badge="SCHEDULED: PART 6"
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-1">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Landmark className="h-4 w-4 text-blue-400" />
              Fed Funds Target
            </span>
            <div className="text-xs text-slate-500 italic font-mono pt-1">Model Pending (G6)</div>
          </CardContent>
        </Card>
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-1">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Percent className="h-4 w-4 text-purple-400" />
              10Y - 2Y Spread
            </span>
            <div className="text-xs text-slate-500 italic font-mono pt-1">Model Pending (G6)</div>
          </CardContent>
        </Card>
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-1">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <TrendingDown className="h-4 w-4 text-amber-400" />
              Core CPI / PCE
            </span>
            <div className="text-xs text-slate-500 italic font-mono pt-1">Model Pending (G6)</div>
          </CardContent>
        </Card>
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-1">
            <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Globe className="h-4 w-4 text-emerald-400" />
              Macro Regime State
            </span>
            <div className="text-xs text-slate-500 italic font-mono pt-1">Classification Inactive</div>
          </CardContent>
        </Card>
      </div>

      <EmptyState
        icon={<Globe className="h-6 w-6 text-purple-400" />}
        title="Macroeconomic Regime Engine Pending"
        description="Sovereign economic series and probabilistic regime classification algorithms (expansion, slowdown, stagflation, recession) will be introduced in Part 6."
      />
    </div>
  );
}
