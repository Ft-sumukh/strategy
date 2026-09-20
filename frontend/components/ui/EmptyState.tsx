import React from 'react';
import { Database, PlusCircle, Play } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  showStandardActions?: boolean;
  onConnectData?: () => void;
  onUseDemoData?: () => void;
}

export function EmptyState({
  title = "Market data isn't connected yet.",
  description = "Connect a supported market-data provider or load the historical demo dataset to begin.",
  icon,
  action,
  showStandardActions = false,
  onConnectData,
  onUseDemoData,
  className,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center rounded-xl border border-dashed border-border/80 bg-surface/30',
        className
      )}
      {...props}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-900 border border-border text-slate-400 mb-3">
        {icon || <Database className="h-6 w-6 text-blue-400" />}
      </div>
      <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
      <p className="mt-1 text-xs text-slate-400 max-w-md">{description}</p>

      {showStandardActions && !action && (
        <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
          <Button
            size="sm"
            variant="primary"
            onClick={onConnectData}
            className="flex items-center gap-1.5 text-xs"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            <span>Connect Data</span>
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={onUseDemoData}
            className="flex items-center gap-1.5 text-xs"
          >
            <Play className="h-3.5 w-3.5" />
            <span>Use Demo Dataset</span>
          </Button>
        </div>
      )}

      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
