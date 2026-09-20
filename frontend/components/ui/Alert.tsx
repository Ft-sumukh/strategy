import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import { cn } from '../../lib/utils';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'destructive';
  title?: string;
}

export function Alert({
  className,
  variant = 'info',
  title,
  children,
  ...props
}: AlertProps) {
  const configs = {
    info: {
      border: 'border-blue-900/60 bg-blue-950/20 text-blue-300',
      icon: <Info className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />,
    },
    success: {
      border: 'border-emerald-900/60 bg-emerald-950/20 text-emerald-300',
      icon: <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />,
    },
    warning: {
      border: 'border-amber-900/60 bg-amber-950/20 text-amber-300',
      icon: <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />,
    },
    destructive: {
      border: 'border-rose-900/60 bg-rose-950/20 text-rose-300',
      icon: <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 shrink-0" />,
    },
  };

  const current = configs[variant];

  return (
    <div
      role="alert"
      className={cn(
        'flex gap-3 rounded-xl border p-4 text-sm leading-relaxed',
        current.border,
        className
      )}
      {...props}
    >
      {current.icon}
      <div className="space-y-1">
        {title && <h5 className="font-semibold leading-none tracking-tight">{title}</h5>}
        <div className="text-xs opacity-90">{children}</div>
      </div>
    </div>
  );
}
