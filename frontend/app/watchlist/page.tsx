'use client';

import React from 'react';
import { Star, Plus } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { EmptyState } from '../../components/ui/EmptyState';
import { Button } from '../../components/ui/Button';

export default function WatchlistPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Asset Watchlists & Pinned Telemetry"
        subtitle="Monitor priority stocks, benchmark indices, and custom asset baskets with real-time alerts."
        badge="SCHEDULED: PART 2"
        actions={
          <Button size="sm" variant="primary" className="flex items-center gap-1.5 text-xs">
            <Plus className="h-3.5 w-3.5" />
            <span>Add Symbol</span>
          </Button>
        }
      />

      <EmptyState
        icon={<Star className="h-6 w-6 text-amber-400" />}
        title="Watchlist Empty"
        description="Pin stocks, indices, and quantitative factor baskets to your custom watchlists once the market data layer is connected."
        showStandardActions
      />
    </div>
  );
}
