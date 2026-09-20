/**
 * AEGIS INVEST — Global Configuration Constants
 */

export const APP_METADATA = {
  name: 'AEGIS INVEST',
  description: 'AI-assisted, risk-aware investment decision-intelligence platform',
  version: '0.1.0',
  currentGroup: 'Group 1 (System Architecture & Repository Foundation)',
} as const;

export const API_ENDPOINTS = {
  HEALTH: '/health',
  READINESS: '/readiness',
  SYSTEM_INFO: '/system/info',
} as const;

export const FINANCIAL_SAFETY = {
  DISCLAIMER_TEXT:
    'AEGIS INVEST is an advanced analytical decision-intelligence research platform. All analytics, metrics, estimates, and scenario evaluations are provided solely for research, informational, and educational purposes. AEGIS does not provide investment advisory services or guarantee financial profits, minimum losses, or specific outcomes. Investing in securities involves substantial risk of loss.',
  NO_DATA_LABEL: 'Data Unavailable (unknown)',
  PROHIBITED_CLAIMS: [
    'guaranteed profit',
    'guaranteed returns',
    'minimum loss',
    'risk-free investing',
    'guaranteed prediction accuracy',
  ],
} as const;
