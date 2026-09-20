'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  TrendingUp,
  Filter,
  Layers,
  FileText,
  Newspaper,
  Globe,
  GitBranch,
  PlayCircle,
  ShieldAlert,
  Zap,
  Briefcase,
  Star,
  Bell,
  Cpu,
  FlaskConical,
  Boxes,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '../../lib/utils';

export interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Markets', href: '/markets', icon: TrendingUp },
  { name: 'Screener', href: '/screener', icon: Filter },
  { name: 'Stocks', href: '/stocks', icon: Layers },
  { name: 'Research', href: '/research', icon: FileText },
  { name: 'News', href: '/news', icon: Newspaper },
  { name: 'Macro', href: '/macro', icon: Globe },
  { name: 'Strategies', href: '/strategies', icon: GitBranch },
  { name: 'Backtesting', href: '/backtesting', icon: PlayCircle },
  { name: 'Risk', href: '/risk', icon: ShieldAlert },
  { name: 'Stress Test', href: '/stress-test', icon: Zap },
  { name: 'Portfolio', href: '/portfolio', icon: Briefcase },
  { name: 'Watchlist', href: '/watchlist', icon: Star },
  { name: 'Alerts', href: '/alerts', icon: Bell },
  { name: 'AI Research', href: '/ai-research', icon: Cpu, badge: 'AI' },
  { name: 'Experiments', href: '/experiments', icon: FlaskConical },
  { name: 'Models', href: '/models', icon: Boxes },
  { name: 'Settings', href: '/settings', icon: Settings },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export function Sidebar({ collapsed: externalCollapsed, onToggleCollapse }: SidebarProps) {
  const pathname = usePathname();
  const [internalCollapsed, setInternalCollapsed] = useState(false);

  const isCollapsed = externalCollapsed !== undefined ? externalCollapsed : internalCollapsed;
  const toggleCollapse = onToggleCollapse || (() => setInternalCollapsed(!internalCollapsed));

  return (
    <aside
      className={cn(
        'relative flex flex-col border-r border-border bg-[#0B0F19] transition-all duration-300 ease-in-out select-none',
        isCollapsed ? 'w-16' : 'w-64'
      )}
      aria-label="Sidebar Navigation"
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border/80">
        <Link href="/dashboard" className="flex items-center gap-2.5 overflow-hidden">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white font-bold shadow-md shadow-blue-600/30">
            A
          </div>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="text-sm font-bold tracking-wider text-white">
                AEGIS <span className="text-blue-400 font-extrabold">INVEST</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-tight">
                DECISION INTELLIGENCE
              </span>
            </div>
          )}
        </Link>
        <button
          onClick={toggleCollapse}
          className="hidden md:flex h-6 w-6 items-center justify-center rounded border border-border/80 bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-700/60 transition-colors"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronLeft className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5 scrollbar-thin">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              title={isCollapsed ? item.name : undefined}
              className={cn(
                'group flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium transition-colors',
                isActive
                  ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                  : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'
              )}
            >
              <Icon
                className={cn(
                  'h-4 w-4 shrink-0 transition-transform duration-200',
                  isActive ? 'text-blue-400' : 'text-slate-400 group-hover:text-slate-200',
                  !isCollapsed && 'group-hover:scale-110'
                )}
              />
              {!isCollapsed && (
                <span className="flex-1 truncate tracking-tight">{item.name}</span>
              )}
              {!isCollapsed && item.badge && (
                <span className="rounded bg-blue-500/20 px-1.5 py-0.5 text-[9px] font-mono font-semibold text-blue-300 border border-blue-500/30">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Institutional Compliance Footer */}
      {!isCollapsed ? (
        <div className="p-3 border-t border-border/80 bg-slate-950/40">
          <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
            <span className="truncate">FOUNDATION ENGINE v0.1.0</span>
          </div>
          <p className="mt-1 text-[10px] text-slate-400 leading-tight">
            Institutional Research & Decision Support
          </p>
        </div>
      ) : (
        <div className="p-2 border-t border-border/80 flex justify-center text-emerald-400" title="Foundation Engine v0.1.0">
          <ShieldCheck className="h-4 w-4" />
        </div>
      )}
    </aside>
  );
}
