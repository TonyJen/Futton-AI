const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '');

const mode = import.meta.env.MODE;
const isProduction = mode === 'production';

const rawApiBaseUrl = import.meta.env.VITE_API_URL || (isProduction ? '/api/v1' : 'http://localhost:8000/api/v1');

export const appConfig = {
  environment: import.meta.env.VITE_APP_ENV || (isProduction ? 'production' : 'development'),
  isProduction,
  apiBaseUrl: trimTrailingSlash(rawApiBaseUrl),
  apiSlowRequestThresholdMs: Number(import.meta.env.VITE_API_SLOW_REQUEST_MS || 1000),
  runtimeMonitoringUrl: import.meta.env.VITE_RUNTIME_MONITORING_URL || '',
  logRuntimeEvents: import.meta.env.DEV || import.meta.env.VITE_LOG_RUNTIME_EVENTS === 'true',
} as const;
