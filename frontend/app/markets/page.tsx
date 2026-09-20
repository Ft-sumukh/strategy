'use client';

import React from 'react';
import { TrendingUp, BarChart2, Globe2 } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Card, CardContent } from '../../components/ui/Card';

export default function MarketsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Global Markets Overview"
        subtitle="Cross-asset performance, index breadth, sector heatmaps, and liquidity conditions."
        badge="SCHEDULED: PART 2"
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-5 space-y-2">
            <div className="flex items-center gap-2 text-slate-300 font-semibold text-xs">
              <TrendingUp className="h-4 w-4 text-emerald-400" />
              Equities & Benchmarks
            </div>
            <p className="text-[11px] text-slate-400">
              S&P 500, NASDAQ-100, Dow Jones, Russell 2000 multi-timeframe tracking.
            </p>
          </CardContent>
        </Card>
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-5 space-y-2">
            <div className="flex items-center gap-2 text-slate-300 font-semibold text-xs">
              <BarChart2 className="h-4 w-4 text-blue-400" />
              Sector Performance
            </div>
            <p className="text-[11px] text-slate-400">
              GICS 11-sector dispersion and relative momentum analysis.
            </p>
          </CardContent>
        </Card>
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-5 space-y-2">
            <div className="flex items-center gap-2 text-slate-300 font-semibold text-xs">
              <Globe2 className="h-4 w-4 text-purple-400" />
              Fixed Income & Commodities
            </div>
            <p className="text-[11px] text-slate-400">
              10Y Treasury, Crude Oil (WTI/Brent), Gold, and Currency crosses.
            </p>
          </CardContent>
        </Card>
      </div>

      <EmptyState
        title="Market Data Pipeline Pending"
        description="Real-time and historical multi-asset market data integration is scheduled for Part 2 (Market Data Layer). Architectural boundaries are fully established."
        showStandardActions
      />
    </div>
  );
}
