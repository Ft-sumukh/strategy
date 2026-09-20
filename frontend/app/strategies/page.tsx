'use client';

import React from 'react';
import { GitBranch, Plus, Trophy } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function StrategiesPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Quantitative Strategy Engine"
        subtitle="Formulate systematic alpha models, rules-based factor strategies, and cross-strategy tournament benchmarks."
        badge="SCHEDULED: PART 7"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <Plus className="h-3.5 w-3.5" />
            <span>New Strategy</span>
          </Button>
        }
      />

      <EmptyState
        icon={<GitBranch className="h-6 w-6 text-purple-400" />}
        title="No Quantitative Strategies Registered"
        description="Strategy formulation, parameter optimization, and Strategy Tournament ranking models are scheduled for Part 7."
      />
    </div>
  );
}
