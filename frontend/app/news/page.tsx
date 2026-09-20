'use client';

import React from 'react';
import { Newspaper, MessageSquare, Radio } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { FilterBar } from '../../components/ui/FilterBar';

export default function NewsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Financial News & Sentiment Intelligence"
        subtitle="Real-time news headlines, SEC filing alerts (8-K, 10-Q), and NLP-driven sentiment analytics."
        badge="SCHEDULED: PART 5"
      />

      <FilterBar
        options={[
          { label: 'All News', value: 'all' },
          { label: 'SEC Filings', value: 'filings' },
          { label: 'Earnings Transcripts', value: 'transcripts' },
          { label: 'Macro & Central Banks', value: 'macro' },
        ]}
        activeValue="all"
        onChange={() => {}}
      />

      <EmptyState
        icon={<Radio className="h-6 w-6 text-cyan-400" />}
        title="News Ingestion Stream Offline"
        description="Multi-source news feeds, sentiment extraction, and financial entity tagging pipelines will be activated in Part 5."
      />
    </div>
  );
}
