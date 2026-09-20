import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';
import { Button } from './Button';
import { cn } from '../../lib/utils';

interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  requestId?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'Service Unavailable',
  message,
  requestId,
  onRetry,
  className,
  ...props
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-6 text-center rounded-xl border border-rose-900/40 bg-rose-950/10',
        className
      )}
      {...props}
    >
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-rose-900/30 text-rose-400 mb-3">
        <AlertCircle className="h-5 w-5" />
      </div>
      <h4 className="text-sm font-semibold text-rose-300">{title}</h4>
      <p className="mt-1 text-xs text-slate-400 max-w-md">{message}</p>
      {requestId && (
        <span className="mt-2 text-[10px] font-mono text-slate-500">
          Request ID: {requestId}
        </span>
      )}
      {onRetry && (
        <Button
          variant="secondary"
          size="sm"
          onClick={onRetry}
          className="mt-4 gap-1.5"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Retry Connection
        </Button>
      )}
    </div>
  );
}
