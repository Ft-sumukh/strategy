import React from 'react';
import { FinancialDisclaimer } from '../disclaimer/FinancialDisclaimer';
import { config } from '../../lib/config';

export function Footer() {
  return (
    <footer className="border-t border-border/80 bg-surface/40 mt-16 pb-12 pt-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <FinancialDisclaimer />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 pt-4 border-t border-border/40">
          <p>
            &copy; {new Date().getFullYear()} {config.appName} Platform. All rights reserved.
          </p>
          <div className="flex items-center gap-4 text-[11px] font-mono">
            <span>Group 1: Foundation</span>
            <span>•</span>
            <span>API Version: {config.appVersion}</span>
            <span>•</span>
            <a
              href={`${config.apiBaseUrl.replace('/api/v1', '')}/docs`}
              target="_blank"
              rel="noreferrer"
              className="text-blue-400 hover:underline"
            >
              OpenAPI Docs
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
