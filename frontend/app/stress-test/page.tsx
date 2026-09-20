'use client';

import React from 'react';
import { Zap, AlertTriangle, ShieldCheck } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { FilterBar } from '../../components/ui/FilterBar';

export default function StressTestPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Scenario Shock & Stress Testing"
        subtitle="Simulate extreme market drawdowns, historical crisis replay (2008 GFC, 2020 COVID), and hypothetical rate shock scenarios."
        badge="SCHEDULED: PART 9"
      />

      <FilterBar
        options={[
          { label: 'All Scenarios', value: 'all' },
          { label: 'Historical Crises', value: 'historical' },
          { label: 'Macro Interest Rate Shocks', value: 'rate_shock' },
          { label: 'Commodity Spikes', value: 'commodity' },
        ]}
        activeValue="all"
        onChange={() => {}}
      />

      <EmptyState
        icon={<Zap className="h-6 w-6 text-rose-400" />}
        title="Stress Scenario Generator Inactive"
        description="Historical crisis replay scenarios and multi-factor stress shock engines will be integrated in Part 9 (Risk Engine & Scenario Stress Testing)."
      />
    </div>
  );
}
