'use client';

import React, { useState } from 'react';
import { Sidebar } from '../navigation/Sidebar';
import { Topbar } from '../navigation/Topbar';
import { FinancialDisclaimer } from '../disclaimer/FinancialDisclaimer';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#070A11] text-slate-100 font-sans selection:bg-blue-600/30 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Viewport */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Topbar Navigation */}
        <Topbar onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)} />

        {/* Scrollable Work Area */}
        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-8 space-y-6 scrollbar-thin">
          {/* Global Disclaimer Header */}
          <FinancialDisclaimer compact />

          {/* Page Content */}
          <div className="max-w-7xl mx-auto w-full pb-12">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
