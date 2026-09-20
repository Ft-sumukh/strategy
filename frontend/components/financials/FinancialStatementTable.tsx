'use client';

import React, { useState } from 'react';
import { IncomeStatementItem, BalanceSheetItem, CashFlowStatementItem } from '../../lib/api/financials';
import { FileText, ChevronRight, Layers } from 'lucide-react';

interface FinancialStatementTableProps {
  incomeStatements: IncomeStatementItem[];
  balanceSheets: BalanceSheetItem[];
  cashFlows: CashFlowStatementItem[];
}

function formatCurrency(val?: number | null): string {
  if (val === undefined || val === null) return '—';
  const absVal = Math.abs(val);
  const sign = val < 0 ? '-' : '';
  if (absVal >= 1_000_000_000) {
    return `${sign}$${(absVal / 1_000_000_000).toFixed(2)}B`;
  }
  if (absVal >= 1_000_000) {
    return `${sign}$${(absVal / 1_000_000).toFixed(2)}M`;
  }
  return `${sign}$${absVal.toLocaleString()}`;
}

function formatPerShare(val?: number | null): string {
  if (val === undefined || val === null) return '—';
  return `$${val.toFixed(2)}`;
}

export const FinancialStatementTable: React.FC<FinancialStatementTableProps> = ({
  incomeStatements,
  balanceSheets,
  cashFlows,
}) => {
  const [activeTab, setActiveTab] = useState<'income' | 'balance' | 'cash_flow'>('income');

  // Sort periods chronologically for table columns (older on left, latest on right, or latest on left)
  // Institutional standard: latest on left
  const sortedIncome = [...incomeStatements].sort((a, b) => b.period.localeCompare(a.period));
  const sortedBalance = [...balanceSheets].sort((a, b) => b.period.localeCompare(a.period));
  const sortedCashFlow = [...cashFlows].sort((a, b) => b.period.localeCompare(a.period));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
      {/* Statement Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-3 bg-slate-950/60">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-400" />
          <h3 className="text-sm font-semibold text-slate-100">Standardized Financial Statements</h3>
        </div>
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab('income')}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
              activeTab === 'income' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Income Statement
          </button>
          <button
            onClick={() => setActiveTab('balance')}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
              activeTab === 'balance' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Balance Sheet
          </button>
          <button
            onClick={() => setActiveTab('cash_flow')}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
              activeTab === 'cash_flow' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Cash Flow
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto p-4">
        {activeTab === 'income' && (
          <table className="w-full text-left text-xs text-slate-300 font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2.5 px-3 font-sans font-medium text-slate-200">Line Item (USD)</th>
                {sortedIncome.map((s) => (
                  <th key={s.period} className="py-2.5 px-3 text-right font-semibold text-slate-100">
                    {s.period} {s.period_type === 'TTM' ? '(TTM)' : ''}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr className="bg-slate-800/20 font-semibold text-white">
                <td className="py-2 px-3 font-sans">Total Revenue</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right text-emerald-400">
                    {formatCurrency(s.revenue)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Cost of Revenue</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right">
                    {formatCurrency(s.cost_of_revenue)}
                  </td>
                ))}
              </tr>
              <tr className="bg-slate-800/10 font-medium">
                <td className="py-2 px-3 font-sans">Gross Profit</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right">
                    {formatCurrency(s.gross_profit)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Operating Expenses</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right">
                    {formatCurrency(s.operating_expenses)}
                  </td>
                ))}
              </tr>
              <tr className="bg-slate-800/10 font-medium">
                <td className="py-2 px-3 font-sans">Operating Income (EBIT)</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right text-blue-400">
                    {formatCurrency(s.operating_income)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">EBITDA</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right">
                    {formatCurrency(s.ebitda)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Tax Expense</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right">
                    {formatCurrency(s.tax_expense)}
                  </td>
                ))}
              </tr>
              <tr className="bg-emerald-950/20 font-bold text-white border-t border-emerald-900/40">
                <td className="py-2 px-3 font-sans text-emerald-300">Net Income</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right text-emerald-400">
                    {formatCurrency(s.net_income)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 font-sans text-slate-400">Diluted EPS</td>
                {sortedIncome.map((s) => (
                  <td key={s.period} className="py-2 px-3 text-right font-semibold text-slate-100">
                    {formatPerShare(s.diluted_eps)}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        )}

        {activeTab === 'balance' && (
          <table className="w-full text-left text-xs text-slate-300 font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2.5 px-3 font-sans font-medium text-slate-200">Balance Sheet Item (USD)</th>
                {sortedBalance.map((b) => (
                  <th key={b.period} className="py-2.5 px-3 text-right font-semibold text-slate-100">
                    {b.period}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr className="bg-slate-800/20 font-semibold text-white">
                <td className="py-2 px-3 font-sans">Cash & Cash Equivalents</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right text-emerald-400">
                    {formatCurrency(b.cash_and_equivalents)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Short-Term Investments</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right">
                    {formatCurrency(b.short_term_investments)}
                  </td>
                ))}
              </tr>
              <tr className="bg-slate-800/10 font-medium">
                <td className="py-2 px-3 font-sans">Current Assets</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right">
                    {formatCurrency(b.current_assets)}
                  </td>
                ))}
              </tr>
              <tr className="bg-slate-800/20 font-semibold text-white">
                <td className="py-2 px-3 font-sans">Total Assets</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right text-blue-400">
                    {formatCurrency(b.total_assets)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Current Liabilities</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right">
                    {formatCurrency(b.current_liabilities)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Total Debt</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right text-amber-400">
                    {formatCurrency(b.total_debt)}
                  </td>
                ))}
              </tr>
              <tr className="bg-slate-800/10 font-medium">
                <td className="py-2 px-3 font-sans">Total Liabilities</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right">
                    {formatCurrency(b.total_liabilities)}
                  </td>
                ))}
              </tr>
              <tr className="bg-emerald-950/20 font-bold text-white border-t border-emerald-900/40">
                <td className="py-2 px-3 font-sans text-emerald-300">Shareholders' Equity</td>
                {sortedBalance.map((b) => (
                  <td key={b.period} className="py-2 px-3 text-right text-emerald-400">
                    {formatCurrency(b.shareholders_equity)}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        )}

        {activeTab === 'cash_flow' && (
          <table className="w-full text-left text-xs text-slate-300 font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2.5 px-3 font-sans font-medium text-slate-200">Cash Flow Item (USD)</th>
                {sortedCashFlow.map((c) => (
                  <th key={c.period} className="py-2.5 px-3 text-right font-semibold text-slate-100">
                    {c.period}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr className="bg-slate-800/20 font-semibold text-white">
                <td className="py-2 px-3 font-sans">Operating Cash Flow (OCF)</td>
                {sortedCashFlow.map((c) => (
                  <td key={c.period} className="py-2 px-3 text-right text-emerald-400">
                    {formatCurrency(c.operating_cash_flow)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Capital Expenditure (CapEx)</td>
                {sortedCashFlow.map((c) => (
                  <td key={c.period} className="py-2 px-3 text-right text-amber-400">
                    {formatCurrency(c.capital_expenditure)}
                  </td>
                ))}
              </tr>
              <tr className="bg-emerald-950/20 font-bold text-white border-t border-emerald-900/40">
                <td className="py-2 px-3 font-sans text-emerald-300">Free Cash Flow (FCF)</td>
                {sortedCashFlow.map((c) => (
                  <td key={c.period} className="py-2 px-3 text-right text-emerald-400 font-bold">
                    {formatCurrency(c.free_cash_flow)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Investing Cash Flow</td>
                {sortedCashFlow.map((c) => (
                  <td key={c.period} className="py-2 px-3 text-right">
                    {formatCurrency(c.investing_cash_flow)}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 px-3 pl-6 font-sans text-slate-400">Financing Cash Flow</td>
                {sortedCashFlow.map((c) => (
                  <td key={c.period} className="py-2 px-3 text-right">
                    {formatCurrency(c.financing_cash_flow)}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
