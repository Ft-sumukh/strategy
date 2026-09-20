'use client';

import React from 'react';
import { Settings, Shield, Server, Key, Database } from 'lucide-react';
import { PageHeader } from '../../components/ui/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Platform & System Settings"
        subtitle="Manage environment configuration, external provider API integrations, audit logging, and security controls."
        badge="PART 1 FOUNDATION"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <Server className="h-4 w-4 text-blue-400" />
              API & Environment Configuration
            </div>
            <div className="space-y-2 text-xs font-mono text-slate-300">
              <div className="flex justify-between py-1.5 border-b border-border/50">
                <span className="text-slate-400">Application Name:</span>
                <span className="text-white">AEGIS INVEST</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border/50">
                <span className="text-slate-400">API Version:</span>
                <span className="text-blue-400">v0.1.0 (Foundation)</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border/50">
                <span className="text-slate-400">Default Currency:</span>
                <span className="text-white">USD</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">Default Timezone:</span>
                <span className="text-white">UTC</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-surface/80 border-border/80">
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <Shield className="h-4 w-4 text-emerald-400" />
              Security & Role Access
            </div>
            <div className="space-y-2 text-xs font-mono text-slate-300">
              <div className="flex justify-between py-1.5 border-b border-border/50">
                <span className="text-slate-400">Active Persona:</span>
                <span className="text-emerald-400">RESEARCHER</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border/50">
                <span className="text-slate-400">Secrets Engine:</span>
                <span className="text-white">Environment Vault</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border/50">
                <span className="text-slate-400">Log Sanitization:</span>
                <span className="text-white">Active (Redacting keys)</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">Audit Trail:</span>
                <span className="text-white">PostgreSQL system_audit</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
