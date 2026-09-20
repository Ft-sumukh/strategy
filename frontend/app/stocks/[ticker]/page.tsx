'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  financialsApi,
  CompanyIntelligence,
  FullFundamentals,
  FullValuation,
  FullTechnicals,
  FullFactors,
} from '../../../lib/api/financials';
import { DataProvenanceBar } from '../../../components/financials/DataProvenanceBar';
import { FinancialStatementTable } from '../../../components/financials/FinancialStatementTable';
import { FundamentalScorecardWidget } from '../../../components/financials/FundamentalScorecardWidget';
import { DCFCalculatorWidget } from '../../../components/financials/DCFCalculatorWidget';
import { TechnicalChartWidget } from '../../../components/financials/TechnicalChartWidget';
import { FactorRadarWidget } from '../../../components/financials/FactorRadarWidget';
import {
  ArrowLeft,
  Building2,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  Target,
  Shield,
  Newspaper,
  Bot,
  Layers,
  ExternalLink,
} from 'lucide-react';

export default function StockDetailPage() {
  const params = useParams();
  const ticker = (params?.ticker as string)?.toUpperCase() || 'AAPL';

  const [activeTab, setActiveTab] = useState<
    'overview' | 'fundamentals' | 'valuation' | 'technicals' | 'factors' | 'risk' | 'news' | 'ai_research'
  >('overview');

  const [intelligence, setIntelligence] = useState<CompanyIntelligence | null>(null);
  const [fundamentals, setFundamentals] = useState<FullFundamentals | null>(null);
  const [valuation, setValuation] = useState<FullValuation | null>(null);
  const [technicals, setTechnicals] = useState<FullTechnicals | null>(null);
  const [factors, setFactors] = useState<FullFactors | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const [intelData, fundData, valData, techData, factData] = await Promise.all([
          financialsApi.getCompanyIntelligence(ticker),
          financialsApi.getFundamentals(ticker),
          financialsApi.getValuation(ticker),
          financialsApi.getTechnicals(ticker),
          financialsApi.getFactors(ticker),
        ]);

        if (isMounted) {
          setIntelligence(intelData);
          setFundamentals(fundData);
          setValuation(valData);
          setTechnicals(techData);
          setFactors(factData);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || `Failed to load intelligence data for ${ticker}.`);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadData();
    return () => {
      isMounted = false;
    };
  }, [ticker]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] space-y-4">
        <div className="h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <div className="text-sm font-mono text-slate-400">Loading Aegis Financial Intelligence for {ticker}...</div>
      </div>
    );
  }

  if (error || !intelligence || !fundamentals || !valuation || !technicals || !factors) {
    return (
      <div className="p-8 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
        <div className="text-rose-400 font-bold text-base">Error Loading Asset</div>
        <p className="text-sm text-slate-400">{error || 'Asset records unavailable.'}</p>
        <Link
          href="/screener"
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg"
        >
          <ArrowLeft className="h-4 w-4" /> Return to Screener
        </Link>
      </div>
    );
  }

  const isPositive = intelligence.price_change_24h >= 0;

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Return */}
      <div className="flex items-center justify-between">
        <Link
          href="/screener"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Screener
        </Link>
        <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
          <span>FLAGSHIP DEMO UNIVERSE</span>
          <span>&bull;</span>
          <span className="text-emerald-400">AUDITED SEC STATEMENTS</span>
        </div>
      </div>

      {/* Institutional Asset Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-extrabold text-white font-mono tracking-tight">{intelligence.ticker}</h1>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-800 text-slate-300 font-mono">
                {intelligence.profile.exchange}
              </span>
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-blue-950/80 text-blue-300 border border-blue-800">
                {intelligence.profile.sector}
              </span>
            </div>
            <div className="text-base text-slate-300 font-medium mt-1">{intelligence.profile.name}</div>
            <div className="text-xs text-slate-400 mt-0.5">{intelligence.profile.industry}</div>
          </div>

          {/* Pricing Box */}
          <div className="text-right">
            <div className="text-3xl font-extrabold text-white font-mono">
              ${intelligence.current_price.toFixed(2)}
            </div>
            <div
              className={`inline-flex items-center gap-1 font-mono text-xs font-bold mt-1 ${
                isPositive ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {isPositive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
              {isPositive ? '+' : ''}
              ${intelligence.price_change_24h.toFixed(2)} ({isPositive ? '+' : ''}
              {intelligence.price_change_percent_24h.toFixed(2)}%)
            </div>
          </div>
        </div>

        {/* Data Provenance Bar */}
        <DataProvenanceBar
          dataSource={intelligence.data_provenance.data_source}
          asOfDate={intelligence.data_provenance.as_of_date}
          currency={intelligence.data_provenance.reporting_currency}
          qualityStatus={intelligence.data_provenance.quality_status}
          isSynthetic={intelligence.data_provenance.is_synthetic}
        />
      </div>

      {/* Terminal Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 overflow-x-auto pb-px">
        {[
          { id: 'overview', label: 'Overview', icon: <Layers className="h-4 w-4" /> },
          { id: 'fundamentals', label: 'Fundamentals', icon: <Building2 className="h-4 w-4" /> },
          { id: 'valuation', label: 'Valuation & DCF', icon: <PieChart className="h-4 w-4" /> },
          { id: 'technicals', label: 'Technicals', icon: <Activity className="h-4 w-4" /> },
          { id: 'factors', label: 'Quantitative Factors', icon: <Target className="h-4 w-4" /> },
          { id: 'risk', label: 'Risk (Phase 3)', icon: <Shield className="h-4 w-4 text-slate-500" /> },
          { id: 'news', label: 'News NLP (Phase 3)', icon: <Newspaper className="h-4 w-4 text-slate-500" /> },
          { id: 'ai_research', label: 'AI Agent (Phase 4)', icon: <Bot className="h-4 w-4 text-slate-500" /> },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold whitespace-nowrap border-b-2 transition-all ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-400 bg-blue-500/10 rounded-t-lg'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6 animate-in fade-in duration-150">
          {/* Top Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
              <div className="text-[11px] text-slate-400 font-mono uppercase">Market Capitalization</div>
              <div className="text-xl font-bold text-white font-mono mt-1">
                ${(Number(intelligence.profile.market_cap || 0) / 1_000_000_000).toFixed(1)}B
              </div>
              <div className="text-[11px] text-slate-500 mt-1">Enterprise scale</div>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
              <div className="text-[11px] text-slate-400 font-mono uppercase">P/E Ratio (Diluted)</div>
              <div className="text-xl font-bold text-blue-400 font-mono mt-1">
                {valuation.multiples.pe_ratio ? `${valuation.multiples.pe_ratio.toFixed(1)}x` : '—'}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                FCF Yield: {valuation.multiples.fcf_yield ? `${(valuation.multiples.fcf_yield * 100).toFixed(1)}%` : '—'}
              </div>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
              <div className="text-[11px] text-slate-400 font-mono uppercase">3Y Revenue CAGR</div>
              <div className="text-xl font-bold text-emerald-400 font-mono mt-1">
                {fundamentals.growth.revenue_cagr_3y
                  ? `${(fundamentals.growth.revenue_cagr_3y * 100).toFixed(1)}%`
                  : '—'}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                ROE: {fundamentals.profitability.return_on_equity ? `${(fundamentals.profitability.return_on_equity * 100).toFixed(1)}%` : '—'}
              </div>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
              <div className="text-[11px] text-slate-400 font-mono uppercase">Fundamental Scorecard</div>
              <div className="text-xl font-bold text-white font-mono mt-1">
                {Math.round(fundamentals.scorecard.overall_score)} / 100
              </div>
              <div className="text-[11px] text-amber-400 font-semibold mt-1">
                {fundamentals.scorecard.rating} Tier
              </div>
            </div>
          </div>

          {/* Scorecard Widget Preview */}
          <FundamentalScorecardWidget scorecard={fundamentals.scorecard} />

          {/* Split 2-Column: Technicals & Factors Preview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TechnicalChartWidget technicals={technicals} />
            <FactorRadarWidget factors={factors} />
          </div>
        </div>
      )}

      {/* TAB 2: FUNDAMENTALS */}
      {activeTab === 'fundamentals' && (
        <div className="space-y-6 animate-in fade-in duration-150">
          <FundamentalScorecardWidget scorecard={fundamentals.scorecard} />

          {/* Growth & Profitability Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
              <h4 className="text-xs font-semibold text-slate-200 uppercase font-mono">Growth Metrics</h4>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>YoY Revenue Growth:</span>
                  <span className="text-white font-bold">
                    {fundamentals.growth.revenue_yoy ? `${(fundamentals.growth.revenue_yoy * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>3-Year Revenue CAGR:</span>
                  <span className="text-emerald-400 font-bold">
                    {fundamentals.growth.revenue_cagr_3y ? `${(fundamentals.growth.revenue_cagr_3y * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>YoY EPS Growth:</span>
                  <span className="text-white font-bold">
                    {fundamentals.growth.eps_yoy ? `${(fundamentals.growth.eps_yoy * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
              <h4 className="text-xs font-semibold text-slate-200 uppercase font-mono">Profitability & Margins</h4>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>Gross Margin:</span>
                  <span className="text-white font-bold">
                    {fundamentals.profitability.gross_margin ? `${(fundamentals.profitability.gross_margin * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Operating Margin:</span>
                  <span className="text-blue-400 font-bold">
                    {fundamentals.profitability.operating_margin ? `${(fundamentals.profitability.operating_margin * 100).toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>ROIC (Invested Capital):</span>
                  <span className="text-emerald-400 font-bold">
                    {fundamentals.profitability.return_on_invested_capital
                      ? `${(fundamentals.profitability.return_on_invested_capital * 100).toFixed(1)}%`
                      : '—'}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
              <h4 className="text-xs font-semibold text-slate-200 uppercase font-mono">Balance Sheet Health</h4>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>Debt-to-Equity:</span>
                  <span className="text-white font-bold">
                    {fundamentals.balance_sheet_health.debt_to_equity
                      ? fundamentals.balance_sheet_health.debt_to_equity.toFixed(2)
                      : '—'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Current Ratio:</span>
                  <span className="text-white font-bold">
                    {fundamentals.balance_sheet_health.current_ratio
                      ? fundamentals.balance_sheet_health.current_ratio.toFixed(2)
                      : '—'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Net Position:</span>
                  <span
                    className={`font-bold ${
                      fundamentals.balance_sheet_health.is_net_cash ? 'text-emerald-400' : 'text-amber-400'
                    }`}
                  >
                    {fundamentals.balance_sheet_health.is_net_cash ? 'Net Cash' : 'Net Debt'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Multi-Year Audited Statements Table */}
          <FinancialStatementTable
            incomeStatements={fundamentals.income_statements}
            balanceSheets={fundamentals.balance_sheets}
            cashFlows={fundamentals.cash_flows}
          />
        </div>
      )}

      {/* TAB 3: VALUATION & DCF */}
      {activeTab === 'valuation' && (
        <div className="space-y-6 animate-in fade-in duration-150">
          {/* Multiples & Peer Row */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-center font-mono">
              <div className="text-[10px] text-slate-500">P/E RATIO</div>
              <div className="text-lg font-bold text-white mt-0.5">
                {valuation.multiples.pe_ratio ? `${valuation.multiples.pe_ratio.toFixed(1)}x` : '—'}
              </div>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-center font-mono">
              <div className="text-[10px] text-slate-500">EV / EBITDA</div>
              <div className="text-lg font-bold text-white mt-0.5">
                {valuation.multiples.ev_to_ebitda ? `${valuation.multiples.ev_to_ebitda.toFixed(1)}x` : '—'}
              </div>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-center font-mono">
              <div className="text-[10px] text-slate-500">P/S RATIO</div>
              <div className="text-lg font-bold text-white mt-0.5">
                {valuation.multiples.ps_ratio ? `${valuation.multiples.ps_ratio.toFixed(1)}x` : '—'}
              </div>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-center font-mono">
              <div className="text-[10px] text-slate-500">P/B RATIO</div>
              <div className="text-lg font-bold text-white mt-0.5">
                {valuation.multiples.pb_ratio ? `${valuation.multiples.pb_ratio.toFixed(1)}x` : '—'}
              </div>
            </div>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-center font-mono">
              <div className="text-[10px] text-slate-500">FCF YIELD</div>
              <div className="text-lg font-bold text-emerald-400 mt-0.5">
                {valuation.multiples.fcf_yield ? `${(valuation.multiples.fcf_yield * 100).toFixed(1)}%` : '—'}
              </div>
            </div>
          </div>

          {/* Historical Percentiles Context */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3">
            <h4 className="text-xs font-semibold text-slate-200 uppercase font-mono">
              3-Year Historical Valuation Context & Percentile Rankings
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2 px-3 font-sans">Multiple</th>
                    <th className="py-2 px-3 text-right">Current</th>
                    <th className="py-2 px-3 text-right">3Y Median</th>
                    <th className="py-2 px-3 text-right">3Y Range (Min - Max)</th>
                    <th className="py-2 px-3 text-right">Percentile Rank</th>
                    <th className="py-2 px-3 font-sans">Historical Interpretation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {valuation.historical_context.map((c) => (
                    <tr key={c.metric_name}>
                      <td className="py-2 px-3 font-bold text-slate-200">{c.metric_name}</td>
                      <td className="py-2 px-3 text-right text-blue-400 font-bold">{c.current_value?.toFixed(1)}x</td>
                      <td className="py-2 px-3 text-right text-slate-300">{c.median_3y?.toFixed(1)}x</td>
                      <td className="py-2 px-3 text-right text-slate-400">
                        {c.min_3y?.toFixed(1)}x &ndash; {c.max_3y?.toFixed(1)}x
                      </td>
                      <td className="py-2 px-3 text-right font-bold text-white">
                        {c.percentile_3y !== undefined && c.percentile_3y !== null
                          ? `${c.percentile_3y.toFixed(0)}%`
                          : '—'}
                      </td>
                      <td className="py-2 px-3 font-sans text-slate-400 text-[11px]">{c.interpretation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Interactive DCF Calculator & Sensitivity Matrix */}
          <DCFCalculatorWidget ticker={ticker} initialDCF={valuation.dcf} />
        </div>
      )}

      {/* TAB 4: TECHNICALS */}
      {activeTab === 'technicals' && (
        <div className="space-y-6 animate-in fade-in duration-150">
          <TechnicalChartWidget technicals={technicals} />
        </div>
      )}

      {/* TAB 5: QUANTITATIVE FACTORS */}
      {activeTab === 'factors' && (
        <div className="space-y-6 animate-in fade-in duration-150">
          <FactorRadarWidget factors={factors} />
        </div>
      )}

      {/* TAB 6: RISK (PHASE 3 PLACEHOLDER) */}
      {activeTab === 'risk' && (
        <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4">
          <Shield className="h-10 w-10 text-slate-500 mx-auto" />
          <h3 className="text-base font-semibold text-white">Portfolio Risk & Stress Testing Engine</h3>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            Scheduled for Phase 3. Will feature parametric & historical Value at Risk (VaR), Expected Shortfall (CVaR),
            macro regime sensitivity, and simulated historical market shock scenarios.
          </p>
        </div>
      )}

      {/* TAB 7: NEWS NLP (PHASE 3 PLACEHOLDER) */}
      {activeTab === 'news' && (
        <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4">
          <Newspaper className="h-10 w-10 text-slate-500 mx-auto" />
          <h3 className="text-base font-semibold text-white">Financial News & Sentiment NLP Engine</h3>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            Scheduled for Phase 3. Will ingest real-time RSS/API financial feeds with entity extraction, sentiment scoring,
            and thematic topic modeling.
          </p>
        </div>
      )}

      {/* TAB 8: AI RESEARCH (PHASE 4 PLACEHOLDER) */}
      {activeTab === 'ai_research' && (
        <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4">
          <Bot className="h-10 w-10 text-slate-500 mx-auto" />
          <h3 className="text-base font-semibold text-white">Aegis AI Investment Research & Synthesis Agent</h3>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            Scheduled for Phase 4. Will synthesize cross-pillar evidence (fundamentals, valuation, technicals, macro, and news)
            into deterministic, auditable research memos with strict epistemic safety boundaries.
          </p>
        </div>
      )}
    </div>
  );
}
