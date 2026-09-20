'use client';

import React from 'react';
import { FlaskConical, Plus, GitCompare } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function ExperimentsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Quantitative Research Experiments"
        subtitle="Track statistical factor tests, hypothesis evaluations, feature importance runs, and ML experiments."
        badge="SCHEDULED: PART 11"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <Plus className="h-3.5 w-3.5" />
            <span>New Experiment</span>
          </Button>
        }
      />

      <EmptyState
        icon={<FlaskConical className="h-6 w-6 text-purple-400" />}
        title="No Active Quantitative Experiments"
        description="Hypothesis testing logs, factor decay evaluations, and ML run tracking are scheduled for Part 11."
      />
    </div>
  );
}
