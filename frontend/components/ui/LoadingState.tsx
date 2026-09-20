import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

interface LoadingStateProps {
  message?: string;
  subtext?: string;
  className?: string;
}

export function LoadingState({
  message = 'Retrieving financial data...',
  subtext = 'Connecting to decision intelligence engine',
  className,
}: LoadingStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-12 text-center rounded-xl border border-border bg-surface/40 space-y-3',
        className
      )}
    >
      <Loader2 className="h-6 w-6 text-blue-400 animate-spin" />
      <div className="space-y-1">
        <p className="text-xs font-semibold text-slate-200">{message}</p>
        <p className="text-[11px] text-slate-500 font-mono">{subtext}</p>
      </div>
    </div>
  );
}
