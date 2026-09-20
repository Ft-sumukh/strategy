import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { Card, CardContent } from './Card';
import { cn } from '../../lib/utils';

interface MetricCardProps {
  title: string;
  value?: string | number | null;
  change?: string | number | null;
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  badge?: string;
  emptyText?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function MetricCard({
  title,
  value,
  change,
  trend,
  subtitle,
  badge,
  emptyText = 'Pending Data Integration',
  icon,
  className,
}: MetricCardProps) {
  const isPending = value === undefined || value === null;

  return (
    <Card className={cn('bg-surface/80 border-border/80 relative overflow-hidden', className)}>
      <CardContent className="p-4 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-slate-400">{title}</span>
          <div className="flex items-center gap-1.5">
            {badge && (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-border/60">
                {badge}
              </span>
            )}
            {icon && <span className="text-slate-500">{icon}</span>}
          </div>
        </div>

        {isPending ? (
          <div className="py-1">
            <span className="text-xs text-slate-500 italic font-mono">{emptyText}</span>
          </div>
        ) : (
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono tracking-tight text-white">
              {value}
            </span>
            {change !== undefined && change !== null && (
              <div
                className={cn(
                  'flex items-center text-xs font-mono font-medium',
                  trend === 'up'
                    ? 'text-emerald-400'
                    : trend === 'down'
                    ? 'text-rose-400'
                    : 'text-slate-400'
                )}
              >
                {trend === 'up' && <ArrowUpRight className="h-3.5 w-3.5 mr-0.5" />}
                {trend === 'down' && <ArrowDownRight className="h-3.5 w-3.5 mr-0.5" />}
                {trend === 'neutral' && <Minus className="h-3.5 w-3.5 mr-0.5" />}
                <span>{change}</span>
              </div>
            )}
          </div>
        )}

        {subtitle && <p className="text-[11px] text-slate-400">{subtitle}</p>}
      </CardContent>
    </Card>
  );
}
