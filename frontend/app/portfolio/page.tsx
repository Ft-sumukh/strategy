'use client';

import React from 'react';
import { Briefcase, Plus, PieChart } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function PortfolioPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Portfolio Construction & Optimization"
        subtitle="Manage asset allocations, enforce factor risk constraints, and execute mean-variance or Black-Litterman optimizations."
        badge="SCHEDULED: PART 10"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <Plus className="h-3.5 w-3.5" />
            <span>Create Portfolio</span>
          </Button>
        }
      />

      <EmptyState
        icon={<Briefcase className="h-6 w-6 text-emerald-400" />}
        title="No Portfolios Configured"
        description="Portfolio entity definitions, position tracking, cash balance management, and risk-constrained optimizers are scheduled for Part 10."
      />
    </div>
  );
}
