import React from 'react';
import { cn } from '../../lib/utils';

export interface FilterOption {
  label: string;
  value: string;
}

interface FilterBarProps {
  options: FilterOption[];
  activeValue: string;
  onChange: (value: string) => void;
  className?: string;
}

export function FilterBar({ options, activeValue, onChange, className }: FilterBarProps) {
  return (
    <div className={cn('flex items-center gap-1.5 overflow-x-auto p-1 bg-slate-900/60 rounded-lg border border-border/60', className)}>
      {options.map((opt) => {
        const isActive = activeValue === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            className={cn(
              'px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors',
              isActive
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            )}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
