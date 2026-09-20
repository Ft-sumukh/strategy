/**
 * AEGIS INVEST — Shared Type Definitions & API Contracts
 * Authoritative TypeScript representations of Backend Pydantic Schemas.
 */

// -----------------------------------------------------------------------------
// System & Health Contracts
// -----------------------------------------------------------------------------
export interface HealthResponse {
  status: 'ok';
  service: string;
  version: string;
  timestamp: string;
}

export type ComponentHealthState = 'ok' | 'degraded' | 'unavailable' | 'disabled';

export interface ComponentStatus {
  status: ComponentHealthState;
  latency_ms?: number | null;
  details?: string | null;
}

export interface ReadinessResponse {
  status: 'ok' | 'degraded' | 'unavailable';
  service: string;
  version: string;
  timestamp: string;
  components: Record<string, ComponentStatus>;
}

export interface SystemTelemetry {
  uptime_seconds: number;
  total_requests: number;
  total_errors: number;
  status_codes: Record<string, number>;
  avg_latency_ms: number;
}

export interface SystemInfoResponse {
  service: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  telemetry: SystemTelemetry;
}

// -----------------------------------------------------------------------------
// Error & Envelope Contracts
// -----------------------------------------------------------------------------
export interface ErrorDetail {
  field?: string | null;
  message: string;
  type?: string | null;
}

export interface ErrorBody {
  code: string;
  message: string;
  details: ErrorDetail[];
  request_id: string;
  timestamp: string;
}

export interface ErrorResponse {
  error: ErrorBody;
}

export interface APIResponse<T> {
  data: T;
  request_id?: string;
  timestamp: string;
}

// -----------------------------------------------------------------------------
// Financial Safety & Research Contracts
// -----------------------------------------------------------------------------
export type FinancialDataModality =
  | 'historical_observation'
  | 'model_output'
  | 'backtest_result'
  | 'hypothetical_scenario'
  | 'prediction'
  | 'user_assumption';

export interface FinancialDisclaimerConfig {
  title: string;
  statement: string;
  regulatoryJurisdiction: string;
  lastUpdated: string;
}

export interface MarketQuoteContract {
  symbol: string;
  bid: number | null;
  ask: number | null;
  last_price: number | null;
  volume: number | null;
  timestamp: string;
  provider: string;
  is_realtime: boolean;
}
