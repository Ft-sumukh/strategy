'use client';

import React from 'react';
import {
  Activity,
  DollarSign,
  ShieldAlert,
  Compass,
  BarChart3,
  TrendingUp,
  Flame,
  Percent,
  Star,
  Newspaper,
  Cpu,
  PieChart,
  Sliders,
  Bell,
  RefreshCw,
} from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { MetricCard } from '../../components/ui/MetricCard';
import { EmptyState } from '../../components/ui/EmptyState';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* Page Header */}
      <PageHeader
        title="Executive Intelligence Dashboard"
        subtitle="Cross-asset market status, portfolio exposure, quantitative regimes, and risk oversight."
        badge="PART 1 FOUNDATION"
        actions={
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="secondary"
              className="flex items-center gap-1.5 text-xs"
              onClick={() => alert('Market data ingestion engine is scheduled for Part 2.')}
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Refresh Telemetry</span>
            </Button>
          </div>
        }
      />

      {/* ==================================================================== */}
      {/* ROW 1: Market Status | Portfolio Value | Portfolio Risk | Market Regime */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Market Status"
          value="DEMO MODE"
          trend="neutral"
          subtitle="US Equities / Global Indices"
          badge="SIMULATED"
          icon={<Activity className="h-4 w-4 text-emerald-400" />}
        />
        <MetricCard
          title="Portfolio Value"
          value={null}
          emptyText="Portfolio engine pending (G10)"
          subtitle="Base Currency: USD"
          icon={<DollarSign className="h-4 w-4 text-blue-400" />}
        />
        <MetricCard
          title="Portfolio Risk (95% VaR)"
          value={null}
          emptyText="Risk engine pending (G9)"
          subtitle="Parametric 1-Day Horizon"
          icon={<ShieldAlert className="h-4 w-4 text-amber-400" />}
        />
        <MetricCard
          title="Market Regime"
          value={null}
          emptyText="Regime model pending (G6)"
          subtitle="Macro & Volatility State"
          icon={<Compass className="h-4 w-4 text-purple-400" />}
        />
      </div>

      {/* ==================================================================== */}
      {/* ROW 2: Major Indices | Market Breadth | Volatility | Rates           */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-blue-400" />
                Major Indices
              </span>
              <span className="text-[10px] font-mono text-slate-500">SPY • QQQ • DIA</span>
            </div>
            <EmptyState
              title="Market data isn't connected yet."
              description="Historical price feeds and benchmark quotes will be ingested in Part 2."
              showStandardActions
              onConnectData={() => alert('Connect Data dialogue will link real providers in Part 2.')}
              onUseDemoData={() => alert('Historical demo dataset initialized for development.')}
              className="py-6"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-emerald-400" />
                Market Breadth
              </span>
              <span className="text-[10px] font-mono text-slate-500">A/D LINE</span>
            </div>
            <EmptyState
              title="Breadth analytics pending"
              description="Advance/Decline ratios and sector net highs will be calculated in Part 4."
              className="py-6"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Flame className="h-4 w-4 text-amber-400" />
                Volatility Structure
              </span>
              <span className="text-[10px] font-mono text-slate-500">VIX / VVIX</span>
            </div>
            <EmptyState
              title="Volatility surface pending"
              description="Term structure and implied volatility metrics will be connected in Part 4."
              className="py-6"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Percent className="h-4 w-4 text-purple-400" />
                Rates & Yield Curve
              </span>
              <span className="text-[10px] font-mono text-slate-500">2Y • 10Y • 30Y</span>
            </div>
            <EmptyState
              title="Treasury curve pending"
              description="Sovereign rates and spread curves will be integrated in Part 6 (Macro)."
              className="py-6"
            />
          </CardContent>
        </Card>
      </div>

      {/* ==================================================================== */}
      {/* ROW 3: Watchlist | Recent News | AI Research                          */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Star className="h-4 w-4 text-amber-400" />
                Flagship Watchlist
              </span>
              <span className="text-[10px] font-mono text-slate-500">0 Assets</span>
            </div>
            <EmptyState
              title="No assets pinned to watchlist"
              description="Track tickers and key metrics once the market data engine is active."
              action={
                <Button size="sm" variant="secondary" className="text-xs">
                  Create Watchlist
                </Button>
              }
              className="py-8"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Newspaper className="h-4 w-4 text-cyan-400" />
                Recent Financial News
              </span>
              <span className="text-[10px] font-mono text-slate-500">NLP Feed</span>
            </div>
            <EmptyState
              title="News stream disconnected"
              description="Financial headlines and NLP sentiment analysis scheduled for Part 5."
              className="py-8"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Cpu className="h-4 w-4 text-blue-400" />
                AI Investment Research
              </span>
              <span className="text-[10px] font-mono text-blue-400">LLM REASONING</span>
            </div>
            <EmptyState
              title="AI research engine pending"
              description="Multi-source synthesis and evidence-backed theses scheduled for Part 11."
              className="py-8"
            />
          </CardContent>
        </Card>
      </div>

      {/* ==================================================================== */}
      {/* ROW 4: Portfolio Exposure | Risk Snapshot | Recent Alerts            */}
      {/* ==================================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <PieChart className="h-4 w-4 text-emerald-400" />
                Portfolio Exposure
              </span>
              <span className="text-[10px] font-mono text-slate-500">SECTOR ALLOCATION</span>
            </div>
            <EmptyState
              title="No active portfolios configured"
              description="Configure portfolio asset weights and constraints in Part 10."
              className="py-8"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Sliders className="h-4 w-4 text-amber-400" />
                Risk Snapshot
              </span>
              <span className="text-[10px] font-mono text-slate-500">STRESS TEST</span>
            </div>
            <EmptyState
              title="Scenario stress testing pending"
              description="Historical replay and parametric shock simulations scheduled for Part 9."
              className="py-8"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <Bell className="h-4 w-4 text-rose-400" />
                Recent Alerts
              </span>
              <span className="text-[10px] font-mono text-slate-500">0 ACTIVE</span>
            </div>
            <EmptyState
              title="No triggered alerts"
              description="Price boundaries, drawdown limits, and anomaly triggers will appear here."
              className="py-8"
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
