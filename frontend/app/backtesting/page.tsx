'use client';

import React from 'react';
import { PlayCircle, History, AlertTriangle } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function BacktestingPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Event-Driven Backtesting Engine"
        subtitle="Simulate historical portfolio execution with realistic slippage, liquidity friction, and transaction cost modeling."
        badge="SCHEDULED: PART 8"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <PlayCircle className="h-3.5 w-3.5" />
            <span>Launch Simulation</span>
          </Button>
        }
      />

      <EmptyState
        icon={<History className="h-6 w-6 text-blue-400" />}
        title="No Backtesting Runs Executed"
        description="Event-driven simulation engines, point-in-time pricing checks, and drawdown analytics are scheduled for Part 8."
      />
    </div>
  );
}
