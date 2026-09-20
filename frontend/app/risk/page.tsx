'use client';

import React from 'react';
import { ShieldAlert, Activity, AlertOctagon } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { MetricCard } from '../../components/ui/MetricCard';

export default function RiskPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Portfolio Risk Analytics & Value-at-Risk"
        subtitle="Parametric, historical, and Monte Carlo Value-at-Risk (VaR), Conditional VaR, and factor drawdown attribution."
        badge="SCHEDULED: PART 9"
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="1-Day 95% Historical VaR"
          value={null}
          emptyText="Risk model inactive"
          subtitle="Confidence: 95.0%"
        />
        <MetricCard
          title="1-Day 99% Conditional VaR (Expected Shortfall)"
          value={null}
          emptyText="Risk model inactive"
          subtitle="Confidence: 99.0%"
        />
        <MetricCard
          title="Portfolio Beta to S&P 500"
          value={null}
          emptyText="Risk model inactive"
          subtitle="Trailing 252 Days"
        />
      </div>

      <EmptyState
        icon={<ShieldAlert className="h-6 w-6 text-amber-400" />}
        title="Risk Engine Offline"
        description="Value-at-Risk calculation matrices, volatility decomposition, and covariance engines are scheduled for Part 9."
      />
    </div>
  );
}
