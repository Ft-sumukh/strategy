'use client';

import React from 'react';
import { Cpu, Sparkles, MessageSquare } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function AIResearchPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Investment Reasoning Engine"
        subtitle="Multi-modal evidence synthesis, automated bull/bear thesis generation, and transparent valuation reasoning."
        badge="SCHEDULED: PART 11"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Generate Synthesis</span>
          </Button>
        }
      />

      <EmptyState
        icon={<Cpu className="h-6 w-6 text-blue-400" />}
        title="AI Reasoning Workspace Offline"
        description="Transparent multi-source evidence synthesis without hallucinations is scheduled for Part 11 (AI Investment Research Workspace)."
      />
    </div>
  );
}
