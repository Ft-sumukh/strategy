import React from 'react';
import { cn } from '../../lib/utils';

export type StatusType = 'healthy' | 'warning' | 'critical' | 'neutral' | 'pending';

interface StatusBadgeProps {
  status: StatusType;
  label: string;
  pulse?: boolean;
  className?: string;
}

export function StatusBadge({ status, label, pulse = false, className }: StatusBadgeProps) {
  const styles: Record<StatusType, { bg: string; text: string; dot: string; border: string }> = {
    healthy: {
      bg: 'bg-emerald-950/40',
      text: 'text-emerald-400',
      dot: 'bg-emerald-400',
      border: 'border-emerald-500/30',
    },
    warning: {
      bg: 'bg-amber-950/40',
      text: 'text-amber-400',
      dot: 'bg-amber-400',
      border: 'border-amber-500/30',
    },
    critical: {
      bg: 'bg-rose-950/40',
      text: 'text-rose-400',
      dot: 'bg-rose-400',
      border: 'border-rose-500/30',
    },
    neutral: {
      bg: 'bg-blue-950/40',
      text: 'text-blue-400',
      dot: 'bg-blue-400',
      border: 'border-blue-500/30',
    },
    pending: {
      bg: 'bg-slate-900/40',
      text: 'text-slate-400',
      dot: 'bg-slate-500',
      border: 'border-slate-700/40',
    },
  };

  const style = styles[status] || styles.neutral;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium font-mono border',
        style.bg,
        style.text,
        style.border,
        className
      )}
    >
      <span className="relative flex h-1.5 w-1.5">
        {pulse && (
          <span
            className={cn('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', style.dot)}
          />
        )}
        <span className={cn('relative inline-flex rounded-full h-1.5 w-1.5', style.dot)} />
      </span>
      {label}
    </span>
  );
}
