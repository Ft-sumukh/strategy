'use client';

import React from 'react';
import { FullTechnicals } from '../../lib/api/financials';
import { Activity, TrendingUp, TrendingDown, Minus, Compass, BarChart2, ShieldAlert } from 'lucide-react';

interface TechnicalChartWidgetProps {
  technicals: FullTechnicals;
}

export const TechnicalChartWidget: React.FC<TechnicalChartWidgetProps> = ({ technicals }) => {
  const getSentimentBadge = (sentiment: string) => {
    if (sentiment === 'BULLISH') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
          <TrendingUp className="h-4 w-4 text-emerald-400" /> BULLISH BIAS
        </span>
      );
    }
    if (sentiment === 'BEARISH') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
          <TrendingDown className="h-4 w-4 text-rose-400" /> BEARISH BIAS
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
        <Minus className="h-4 w-4" /> NEUTRAL
      </span>
    );
  };

  const getSignalBadge = (sig: 'BULLISH' | 'BEARISH' | 'NEUTRAL') => {
    if (sig === 'BULLISH') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950/80 text-emerald-300 border border-emerald-800">
          BULLISH
        </span>
      );
    }
    if (sig === 'BEARISH') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-rose-950/80 text-rose-300 border border-rose-800">
          BEARISH
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-slate-800 text-slate-300 border border-slate-700">
        NEUTRAL
      </span>
    );
  };

  const rsiVal = technicals.rsi.rsi_14 ?? 50;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-purple-400" />
            <h3 className="text-base font-semibold text-white">Institutional Technical Indicators & Signals</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Deterministic quantitative technical indicators computed as of {technicals.as_of_date}
          </p>
        </div>

        <div>{getSentimentBadge(technicals.overall_sentiment)}</div>
      </div>

      {/* Indicator Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* RSI Card */}
        <div className="p-3.5 bg-slate-950/60 rounded-lg border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">RSI (14-Period)</span>
            <span className="font-mono font-bold text-white text-sm">{rsiVal.toFixed(1)}</span>
          </div>

          <div className="space-y-1">
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden relative">
              <div
                className={`h-full transition-all ${
                  rsiVal >= 70 ? 'bg-rose-500' : rsiVal <= 30 ? 'bg-emerald-500' : 'bg-blue-500'
                }`}
                style={{ width: `${Math.max(5, Math.min(100, rsiVal))}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>30 Oversold</span>
              <span>70 Overbought</span>
            </div>
          </div>
          <p className="text-[10px] text-slate-400 italic leading-tight">{technicals.rsi.interpretation}</p>
        </div>

        {/* MACD Card */}
        <div className="p-3.5 bg-slate-950/60 rounded-lg border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">MACD (12, 26, 9)</span>
            <span
              className={`font-mono font-bold text-xs ${
                (technicals.macd.histogram ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {technicals.macd.status}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-1 text-[11px] font-mono pt-1 text-center">
            <div className="bg-slate-900 p-1 rounded">
              <div className="text-slate-500 text-[9px]">MACD</div>
              <div className="text-slate-200 font-semibold">{technicals.macd.macd_line?.toFixed(2) ?? '—'}</div>
            </div>
            <div className="bg-slate-900 p-1 rounded">
              <div className="text-slate-500 text-[9px]">SIGNAL</div>
              <div className="text-slate-200 font-semibold">{technicals.macd.signal_line?.toFixed(2) ?? '—'}</div>
            </div>
            <div className="bg-slate-900 p-1 rounded">
              <div className="text-slate-500 text-[9px]">HIST</div>
              <div
                className={`font-semibold ${
                  (technicals.macd.histogram ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {technicals.macd.histogram?.toFixed(2) ?? '—'}
              </div>
            </div>
          </div>
        </div>

        {/* Bollinger Bands Card */}
        <div className="p-3.5 bg-slate-950/60 rounded-lg border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">Bollinger (20, 2&sigma;)</span>
            <span className="font-mono text-slate-300 text-[11px]">
              BW: {((technicals.bollinger.bandwidth ?? 0) * 100).toFixed(1)}%
            </span>
          </div>
          <div className="space-y-1 text-[11px] font-mono">
            <div className="flex justify-between text-slate-400">
              <span>Upper:</span>
              <span className="text-slate-200 font-semibold">${technicals.bollinger.upper_band?.toFixed(2) ?? '—'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Middle (SMA 20):</span>
              <span className="text-slate-200 font-semibold">${technicals.bollinger.middle_band?.toFixed(2) ?? '—'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Lower:</span>
              <span className="text-slate-200 font-semibold">${technicals.bollinger.lower_band?.toFixed(2) ?? '—'}</span>
            </div>
          </div>
        </div>

        {/* Volatility & Trend Card */}
        <div className="p-3.5 bg-slate-950/60 rounded-lg border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 font-medium">Volatility & Trend</span>
            <span className="font-mono text-purple-400 text-[11px] font-bold">
              {technicals.volatility_and_trend.trend_strength}
            </span>
          </div>
          <div className="space-y-1 text-[11px] font-mono">
            <div className="flex justify-between text-slate-400">
              <span>ADX (14):</span>
              <span className="text-slate-200 font-semibold">{technicals.volatility_and_trend.adx_14?.toFixed(1) ?? '—'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>ATR (14):</span>
              <span className="text-slate-200 font-semibold">${technicals.volatility_and_trend.atr_14?.toFixed(2) ?? '—'}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>1Y Ann. Volatility:</span>
              <span className="text-slate-200 font-semibold">
                {technicals.volatility_and_trend.volatility_252d
                  ? `${(technicals.volatility_and_trend.volatility_252d * 100).toFixed(1)}%`
                  : '—'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Moving Averages Grid */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-slate-300 font-sans">Moving Averages Structural Profile</h4>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-center text-xs font-mono">
          <div className="p-2 bg-slate-950 rounded border border-slate-800">
            <div className="text-slate-500 text-[10px]">SMA 20</div>
            <div className="text-slate-200 font-semibold">${technicals.moving_averages.sma_20?.toFixed(2) ?? '—'}</div>
          </div>
          <div className="p-2 bg-slate-950 rounded border border-slate-800">
            <div className="text-slate-500 text-[10px]">SMA 50</div>
            <div className="text-slate-200 font-semibold">${technicals.moving_averages.sma_50?.toFixed(2) ?? '—'}</div>
          </div>
          <div className="p-2 bg-slate-950 rounded border border-slate-800">
            <div className="text-slate-500 text-[10px]">SMA 100</div>
            <div className="text-slate-200 font-semibold">${technicals.moving_averages.sma_100?.toFixed(2) ?? '—'}</div>
          </div>
          <div className="p-2 bg-slate-950 rounded border border-slate-800">
            <div className="text-slate-500 text-[10px]">SMA 200</div>
            <div className="text-blue-400 font-bold">${technicals.moving_averages.sma_200?.toFixed(2) ?? '—'}</div>
          </div>
          <div className="p-2 bg-slate-950 rounded border border-slate-800">
            <div className="text-slate-500 text-[10px]">EMA 12</div>
            <div className="text-slate-200 font-semibold">${technicals.moving_averages.ema_12?.toFixed(2) ?? '—'}</div>
          </div>
          <div className="p-2 bg-slate-950 rounded border border-slate-800">
            <div className="text-slate-500 text-[10px]">EMA 26</div>
            <div className="text-slate-200 font-semibold">${technicals.moving_averages.ema_26?.toFixed(2) ?? '—'}</div>
          </div>
        </div>
      </div>

      {/* Standardized Signals Table */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-slate-300 font-sans">Active Deterministic Technical Signals</h4>
        <div className="overflow-x-auto border border-slate-800 rounded-lg">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 font-mono">
                <th className="py-2.5 px-3">Indicator</th>
                <th className="py-2.5 px-3">Signal</th>
                <th className="py-2.5 px-3">Value</th>
                <th className="py-2.5 px-3">Threshold</th>
                <th className="py-2.5 px-3 font-sans">Institutional Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {technicals.signals.map((s, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-2.5 px-3 font-semibold text-slate-200">{s.indicator}</td>
                  <td className="py-2.5 px-3">{getSignalBadge(s.signal)}</td>
                  <td className="py-2.5 px-3 text-slate-300">{s.value.toFixed(2)}</td>
                  <td className="py-2.5 px-3 text-slate-400">{s.benchmark_threshold}</td>
                  <td className="py-2.5 px-3 font-sans text-slate-300 text-[11px] leading-relaxed">
                    {s.rationale}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
