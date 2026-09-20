/**
 * AEGIS INVEST — Shared Utilities
 */

/**
 * Formats an ISO date string to UTC localized format.
 */
export function formatUTC(dateString: string | Date): string {
  try {
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    if (isNaN(date.getTime())) return 'Invalid date';
    return date.toUTCString();
  } catch {
    return 'Invalid date';
  }
}

/**
 * Formats a number to currency USD or returns 'unknown' if missing.
 * Strict adherence to FINANCIAL SAFETY: Never converts null/undefined to $0.00!
 */
export function formatCurrencySafe(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return 'unknown';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

/**
 * Formats a percentage safe value or returns 'unknown' if missing.
 */
export function formatPercentageSafe(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return 'unknown';
  }
  return `${(value * 100).toFixed(2)}%`;
}
