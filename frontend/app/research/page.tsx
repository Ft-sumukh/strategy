'use client';

import React from 'react';
import { FileText, BookOpen, PenTool } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function ResearchPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Investment Research Workspace"
        subtitle="Analyst theses, valuation models, peer comparables, and structured evidence syntheses."
        badge="SCHEDULED: PART 11"
        actions={
          <Button size="sm" variant="secondary" className="flex items-center gap-1.5 text-xs">
            <PenTool className="h-3.5 w-3.5" />
            <span>New Research Memo</span>
          </Button>
        }
      />

      <EmptyState
        icon={<BookOpen className="h-6 w-6 text-amber-400" />}
        title="Research Workspace Uninitialized"
        description="Analyst memo authoring, valuation template linking, and peer comparison tools will be deployed in Part 11 (Research & AI Workspace)."
      />
    </div>
  );
}
