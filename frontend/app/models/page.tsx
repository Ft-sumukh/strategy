'use client';

import React from 'react';
import { Boxes, Plus, CheckCircle2 } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function ModelsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Predictive & Factor Model Registry"
        subtitle="Manage versioned quantitative factor models, valuation regressions, and machine learning weights."
        badge="SCHEDULED: PART 11"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <Plus className="h-3.5 w-3.5" />
            <span>Register Model</span>
          </Button>
        }
      />

      <EmptyState
        icon={<Boxes className="h-6 w-6 text-emerald-400" />}
        title="Model Registry Empty"
        description="Versioned predictive model artifacts, feature matrices, and calibration records will be housed here in Part 11."
      />
    </div>
  );
}
