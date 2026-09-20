import React from 'react';
import { Shield, Activity, Terminal } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { config } from '../../lib/config';

interface HeaderProps {
  apiStatus?: 'online' | 'offline' | 'checking';
}

export function Header({ apiStatus = 'checking' }: HeaderProps) {
  const statusBadge = {
    online: <Badge variant="success">API v1 Connected</Badge>,
    offline: <Badge variant="danger">API Disconnected</Badge>,
    checking: <Badge variant="info">Probing API...</Badge>,
  }[apiStatus];

  return (
    <header className="border-b border-border/80 bg-surface/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-md shadow-blue-500/20 text-white">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-wider text-base text-white font-mono">
                AEGIS<span className="text-blue-500">.INVEST</span>
              </span>
              <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-mono">
                v{config.appVersion}
              </Badge>
            </div>
            <p className="text-[11px] text-slate-400 font-normal hidden sm:block">
              Risk-Aware Investment Decision-Intelligence
            </p>
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400">
            <Terminal className="w-3.5 h-3.5 text-slate-500" />
            <span className="font-mono text-slate-300">[{config.appEnv}]</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-slate-400" />
            {statusBadge}
          </div>
        </div>
      </div>
    </header>
  );
}
