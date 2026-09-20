import React from 'react';
import { Shield, ArrowRight, Code2, BookOpen, Terminal } from 'lucide-react';
import { SystemHealthStatus } from '../components/system/SystemHealthStatus';
import { ArchitectureMap } from '../components/system/ArchitectureMap';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { FinancialDisclaimer } from '../components/disclaimer/FinancialDisclaimer';

export default function HomePage() {
  return (
    <div className="space-y-8">
      {/* Compact Disclaimer Notice at the top */}
      <FinancialDisclaimer compact />

      {/* Hero / Platform Overview */}
      <div className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-b from-surface/90 via-surface/40 to-background p-6 sm:p-10">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2">
            <Badge variant="info">Phase 1 Delivery</Badge>
            <span className="text-xs text-slate-400 font-mono">Engineering Foundation</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
            AEGIS INVEST <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">
              Decision-Intelligence Platform
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            A serious, production-engineered financial intelligence platform designed for institutional research, risk modeling, and systematic decision support. Built on an API-first, modular architecture engineered for complete auditability and reproducibility.
          </p>

          <div className="pt-3 flex flex-wrap items-center gap-3">
            <a
              href="/dashboard"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition-all"
            >
              <span>Open Executive Dashboard</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-border bg-slate-900/60 hover:bg-slate-800 text-slate-300 text-xs font-semibold transition-all"
            >
              <span>API Documentation</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
          </div>

          <div className="pt-2 flex flex-wrap items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-slate-400">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span>Zero Hallucinated Metrics</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400">
              <Code2 className="w-4 h-4 text-blue-400" />
              <span>Layered Clean Architecture</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400">
              <Terminal className="w-4 h-4 text-purple-400" />
              <span>Deterministic Reproducibility</span>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time System Connectivity Card */}
      <SystemHealthStatus />

      {/* Interactive System Architecture Map */}
      <ArchitectureMap />

      {/* Developer Quick-Start Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-surface/70">
          <CardContent className="p-5 space-y-3">
            <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
              <BookOpen className="w-4 h-4 text-blue-400" />
              <h4>API Documentation</h4>
            </div>
            <p className="text-xs text-slate-400">
              The backend provides interactive OpenAPI documentation with schemas, request ID tracking, and standardized error envelopes.
            </p>
            <div className="pt-2 flex items-center gap-3">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-400 hover:text-blue-300"
              >
                Swagger UI <ArrowRight className="w-3.5 h-3.5" />
              </a>
              <span className="text-slate-600">•</span>
              <a
                href="http://localhost:8000/redoc"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-400 hover:text-blue-300"
              >
                ReDoc <ArrowRight className="w-3.5 h-3.5" />
              </a>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-surface/70">
          <CardContent className="p-5 space-y-3">
            <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
              <Terminal className="w-4 h-4 text-purple-400" />
              <h4>Verification Commands</h4>
            </div>
            <p className="text-xs text-slate-400">
              Execute tests and migrations to verify system integrity:
            </p>
            <div className="bg-slate-950 p-2.5 rounded-lg font-mono text-[11px] text-slate-300 space-y-1">
              <div>$ python -m pytest (18 backend/integration tests)</div>
              <div>$ cd apps/api && alembic upgrade head</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
