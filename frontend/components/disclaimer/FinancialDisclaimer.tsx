import React from 'react';
import { ShieldAlert, Scale, Check } from 'lucide-react';
import { cn } from '../../lib/utils';

interface FinancialDisclaimerProps extends React.HTMLAttributes<HTMLDivElement> {
  compact?: boolean;
}

export function FinancialDisclaimer({
  compact = false,
  className,
  ...props
}: FinancialDisclaimerProps) {
  if (compact) {
    return (
      <div
        className={cn(
          'flex items-center gap-2 p-2.5 rounded-lg border border-border/80 bg-slate-900/60 text-[11px] text-slate-400',
          className
        )}
        {...props}
      >
        <ShieldAlert className="w-4 h-4 text-amber-500/80 shrink-0" />
        <p>
          <span className="font-semibold text-slate-300">Financial Disclaimer:</span> Aegis Invest provides research and decision-support analysis based on historical, market, and modeled data. It does not guarantee future performance or investment outcomes. Model outputs are subject to assumptions, data limitations, and market uncertainty.
        </p>
      </div>
    );
  }

  return (
    <section
      aria-label="Financial and Regulatory Disclaimer"
      className={cn(
        'rounded-xl border border-border bg-surface/50 p-5 space-y-3 text-xs leading-relaxed text-slate-400',
        className
      )}
      {...props}
    >
      <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
        <Scale className="w-4 h-4 text-accent-blue" />
        <h4>Institutional Governance & Research Integrity Principles</h4>
      </div>

      <p>
        <strong className="text-slate-300">No Advisory or Guaranteed Outcomes:</strong> AEGIS INVEST is engineered strictly as an evidence-based, risk-aware decision-intelligence and quantitative research platform. All analytics, historical backtests, scenario simulations, and metrics are furnished exclusively for informational and research purposes. AEGIS explicitly repudiates claims of guaranteed profits, risk-free returns, or bounded maximum drawdowns.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-[11px]">
        <div className="flex gap-2 items-start bg-slate-900/50 p-2.5 rounded-lg border border-border/50">
          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            <strong className="text-slate-300">Data Integrity Policy:</strong> AEGIS never fabricates market data, historical returns, or model outputs. When data is unavailable, it remains explicitly <code>unknown</code>.
          </span>
        </div>
        <div className="flex gap-2 items-start bg-slate-900/50 p-2.5 rounded-lg border border-border/50">
          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            <strong className="text-slate-300">Explicit Modality Separation:</strong> System architecture strictly delineates Historical Observations, Model Outputs, Backtest Results, and Hypothetical Stress Scenarios.
          </span>
        </div>
      </div>
    </section>
  );
}
