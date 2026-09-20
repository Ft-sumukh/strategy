'use client';

import React, { useEffect, useState } from 'react';
import { Database, Server, RefreshCw, Layers, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Skeleton } from '../ui/Skeleton';
import { ErrorState } from '../ui/ErrorState';
import { apiClient } from '../../lib/api/client';
import { HealthResponse, ReadinessResponse, SystemInfoResponse } from '../../lib/api/types';

export function SystemHealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfoResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);
  const [lastCheck, setLastCheck] = useState<string | null>(null);

  const fetchStatus = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [h, r, s] = await Promise.all([
        apiClient.getHealth(),
        apiClient.getReadiness(),
        apiClient.getSystemInfo().catch(() => null),
      ]);
      setHealth(h);
      setReadiness(r);
      setSystemInfo(s);
      setLastCheck(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError({
        message: err.message || 'Failed to connect to AEGIS API',
        requestId: err.requestId,
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  if (error) {
    return (
      <Card className="border-rose-900/50 bg-surface/90">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>System Connectivity Error</CardTitle>
              <CardDescription>Could not reach the AEGIS Backend API</CardDescription>
            </div>
            <Button variant="secondary" size="sm" onClick={fetchStatus} isLoading={isLoading}>
              <RefreshCw className="w-3.5 h-3.5" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ErrorState
            title="API Connection Failed"
            message={error.message}
            requestId={error.requestId}
            onRetry={fetchStatus}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-surface/90">
      <CardHeader>
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div>
            <div className="flex items-center gap-2">
              <CardTitle>Platform Operational Status</CardTitle>
              <Badge variant="success">Active</Badge>
            </div>
            <CardDescription>
              Live health and readiness probes from <code>/api/v1/health</code> & <code>/api/v1/readiness</code>
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            {lastCheck && (
              <span className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
                <Clock className="w-3 h-3" /> Checked: {lastCheck}
              </span>
            )}
            <Button
              variant="secondary"
              size="sm"
              onClick={fetchStatus}
              isLoading={isLoading}
              className="gap-1 text-xs"
            >
              <RefreshCw className="w-3 h-3" />
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {isLoading && !health ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* API Liveness */}
            <div className="p-4 rounded-xl border border-border bg-slate-900/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                  <Server className="w-3.5 h-3.5 text-blue-400" />
                  FastAPI Server
                </span>
                <Badge variant={health?.status === 'ok' ? 'success' : 'danger'}>
                  {health?.status === 'ok' ? 'Alive (200 OK)' : 'Offline'}
                </Badge>
              </div>
              <div className="text-lg font-semibold text-white font-mono">
                {health?.service || 'aegis-api'}
              </div>
              <div className="text-[11px] text-slate-500 flex justify-between">
                <span>Version: v{health?.version || '0.1.0'}</span>
                <span>Liveness Probe</span>
              </div>
            </div>

            {/* PostgreSQL Readiness */}
            <div className="p-4 rounded-xl border border-border bg-slate-900/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-emerald-400" />
                  Database (PostgreSQL/SQLite)
                </span>
                <Badge
                  variant={
                    readiness?.components.database?.status === 'ok' ? 'success' : 'danger'
                  }
                >
                  {readiness?.components.database?.status || 'unknown'}
                </Badge>
              </div>
              <div className="text-lg font-semibold text-white font-mono">
                {readiness?.components.database?.latency_ms != null
                  ? `${readiness.components.database.latency_ms}ms`
                  : 'Connected'}
              </div>
              <div className="text-[11px] text-slate-500 flex justify-between">
                <span>Migration: v0001 (Applied)</span>
                <span>Readiness Probe</span>
              </div>
            </div>

            {/* Telemetry / Infrastructure */}
            <div className="p-4 rounded-xl border border-border bg-slate-900/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-purple-400" />
                  Runtime Telemetry
                </span>
                <Badge variant="info">
                  {systemInfo?.environment || 'development'}
                </Badge>
              </div>
              <div className="text-lg font-semibold text-white font-mono">
                {systemInfo?.uptime_seconds
                  ? `${systemInfo.uptime_seconds}s uptime`
                  : 'Active'}
              </div>
              <div className="text-[11px] text-slate-500 flex justify-between">
                <span>
                  Reqs: {systemInfo?.telemetry?.total_requests ?? 0}
                </span>
                <span>
                  Latency: {systemInfo?.telemetry?.avg_latency_ms ?? 0}ms
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
