'use client';

import React, { useState } from 'react';
import { Search, Bell, User, Wifi } from 'lucide-react';
import { GlobalSearchModal } from '../common/GlobalSearchModal';

interface TopbarProps {
  onToggleSidebar?: () => void;
}

export function Topbar({ onToggleSidebar }: TopbarProps) {
  const [searchOpen, setSearchOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <>
      <header
        className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-[#0B0F19]/95 backdrop-blur px-4 sm:px-6"
        aria-label="Top Navigation Bar"
      >
        {/* Left: Mobile hamburger & Search trigger */}
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            aria-label="Toggle Navigation"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Global Search Input Button */}
          <button
            onClick={() => setSearchOpen(true)}
            className="flex items-center gap-2.5 rounded-lg border border-border bg-slate-900/60 px-3 py-1.5 text-xs text-slate-400 hover:border-slate-700 hover:bg-slate-800/80 transition-all w-64 sm:w-80 text-left group"
          >
            <Search className="h-3.5 w-3.5 text-slate-500 group-hover:text-slate-300" />
            <span className="flex-1 truncate">Search assets, strategies, portfolios...</span>
            <kbd className="hidden sm:inline-flex items-center rounded border border-border px-1.5 py-0.5 text-[10px] font-mono text-slate-500">
              Ctrl+K
            </kbd>
          </button>
        </div>

        {/* Right: Market Status, Notification Icon, User Profile */}
        <div className="flex items-center gap-3">
          {/* Market Status Indicator */}
          <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-2.5 py-1 text-xs">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-[11px] font-semibold text-emerald-400">
              DEMO FEED ACTIVE
            </span>
          </div>

          {/* Infrastructure Health Indicator */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono px-2 py-1 bg-slate-900/40 rounded-lg border border-border/60">
            <Wifi className="h-3.5 w-3.5 text-blue-400" />
            <span className="text-[11px] hidden md:inline">API: READY</span>
          </div>

          {/* Notifications Dropdown */}
          <div className="relative">
            <button
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className="relative p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
              aria-label="View notifications"
            >
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-blue-500" />
            </button>

            {notificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 rounded-xl border border-border bg-[#0B0F19] shadow-2xl p-4 space-y-3 z-50">
                <div className="flex items-center justify-between border-b border-border pb-2">
                  <span className="text-xs font-semibold text-slate-200">System Notifications</span>
                  <span className="text-[10px] font-mono text-slate-500">1 New</span>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-900/80 border border-border/60">
                    <div className="font-medium text-slate-200">Foundation Architecture Ready</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      FastAPI backend and Next.js shell successfully initialized. Market data pipelines pending Part 2.
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* User Profile */}
          <div className="flex items-center gap-2 pl-2 border-l border-border/80">
            <div className="h-7 w-7 rounded-full bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <User className="h-4 w-4" />
            </div>
            <div className="hidden lg:flex flex-col text-left">
              <span className="text-xs font-semibold text-slate-200 leading-none">Research Analyst</span>
              <span className="text-[10px] font-mono text-blue-400 mt-0.5">ROLE: RESEARCHER</span>
            </div>
          </div>
        </div>
      </header>

      {/* Global Search Modal */}
      <GlobalSearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}
