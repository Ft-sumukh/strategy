'use client';

import React from 'react';
import { Bell, Plus, ShieldAlert } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function AlertsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Alerts & Threshold Monitoring"
        subtitle="Manage automated triggers for price levels, volatility spikes, drawdown limits, and model signal changes."
        badge="SCHEDULED: PART 12"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <Plus className="h-3.5 w-3.5" />
            <span>Create Alert Rule</span>
          </Button>
        }
      />

      <EmptyState
        icon={<Bell className="h-6 w-6 text-rose-400" />}
        title="No Active Alert Rules"
        description="Automated signal triggers, risk threshold monitors, and email/webhook dispatchers are scheduled for Part 12."
      />
    </div>
  );
}
