import React from 'react';
import { Layers, ShieldCheck, Database, GitBranch, Cpu, LineChart, FileText, AlertOctagon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/Card';
import { Badge } from '../ui/Badge';

export function ArchitectureMap() {
  const futureModules = [
    { name: 'Market Data Ingestion', icon: <LineChart className="w-4 h-4 text-slate-500" />, desc: 'Real-time & historical tick/bar data with multi-vendor abstraction' },
    { name: 'Fundamental Analysis', icon: <FileText className="w-4 h-4 text-slate-500" />, desc: 'SEC EDGAR 10-K/10-Q parsing, financial ratios, balance sheet health' },
    { name: 'Technical & Quantitative', icon: <Cpu className="w-4 h-4 text-slate-500" />, desc: 'Factor modeling, momentum, mean-reversion, statistical signals' },
    { name: 'Risk & Stress Testing', icon: <AlertOctagon className="w-4 h-4 text-slate-500" />, desc: 'Parametric/Historical VaR, Expected Shortfall, Tail-Risk scenarios' },
    { name: 'Backtesting Engine', icon: <GitBranch className="w-4 h-4 text-slate-500" />, desc: 'Event-driven simulation with realistic slippage, liquidity & latency' },
    { name: 'Portfolio Optimization', icon: <Layers className="w-4 h-4 text-slate-500" />, desc: 'Mean-variance, Black-Litterman, hierarchical risk parity' },
  ];

  return (
    <div className="space-y-6">
      <Card className="bg-surface/90">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>System Architecture & Module Boundaries</CardTitle>
              <CardDescription>
                Clean layered separation of concerns across presentation, API, domain, and persistence
              </CardDescription>
            </div>
            <Badge variant="info">Group 1 Scope</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {/* Presentation */}
            <div className="p-3.5 rounded-xl border border-blue-900/50 bg-blue-950/10 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-blue-400">Presentation</span>
                <Badge variant="success" className="text-[10px]">Active</Badge>
              </div>
              <p className="text-[11px] text-slate-400">
                Next.js 14 App Router, TypeScript strict, centralized API client, responsive dark design tokens.
              </p>
            </div>

            {/* API & Security */}
            <div className="p-3.5 rounded-xl border border-indigo-900/50 bg-indigo-950/10 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-indigo-400">API & Security</span>
                <Badge variant="success" className="text-[10px]">Active</Badge>
              </div>
              <p className="text-[11px] text-slate-400">
                FastAPI v1, Request ID propagation, structured logging, RFC error envelopes, CORS & security headers.
              </p>
            </div>

            {/* Application & Domain */}
            <div className="p-3.5 rounded-xl border border-emerald-900/50 bg-emerald-950/10 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-emerald-400">Application Layer</span>
                <Badge variant="success" className="text-[10px]">Active</Badge>
              </div>
              <p className="text-[11px] text-slate-400">
                Health & readiness evaluation services, repository pattern, provider abstraction interfaces.
              </p>
            </div>

            {/* Persistence & Infra */}
            <div className="p-3.5 rounded-xl border border-purple-900/50 bg-purple-950/10 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-purple-400">Persistence</span>
                <Badge variant="success" className="text-[10px]">Active</Badge>
              </div>
              <p className="text-[11px] text-slate-400">
                SQLAlchemy 2.0 async sessions, Alembic migration tracking, PostgreSQL 16 & Redis containerization.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Future Planned Modules (Honest display - No fake data) */}
      <Card className="bg-surface/50 border-dashed border-border/80">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <CardTitle className="text-slate-300">Future Financial & Quantitative Modules</CardTitle>
                <Badge variant="outline" className="text-[10px]">Planned (Group 2+)</Badge>
              </div>
              <CardDescription>
                Architecturally isolated domains ready to be mounted onto the Group 1 foundation
              </CardDescription>
            </div>
            <ShieldCheck className="w-5 h-5 text-slate-500" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {futureModules.map((m) => (
              <div
                key={m.name}
                className="p-3 rounded-lg border border-border/60 bg-slate-900/30 space-y-1"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {m.icon}
                    <span className="text-xs font-medium text-slate-300">{m.name}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">Deferred</span>
                </div>
                <p className="text-[11px] text-slate-500">{m.desc}</p>
                <div className="pt-1">
                  <span className="text-[10px] text-amber-500/80 font-mono">
                    Coming in a future research module
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
