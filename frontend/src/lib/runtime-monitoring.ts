import { appConfig } from './config';

type RuntimeEventType =
  | 'frontend.error'
  | 'frontend.promise_rejection'
  | 'frontend.navigation'
  | 'frontend.api_timing';

export interface RuntimeEvent {
  type: RuntimeEventType;
  message: string;
  path?: string;
  durationMs?: number;
  statusCode?: number;
  metadata?: Record<string, unknown>;
  timestamp?: string;
}

let initialized = false;

function emitRuntimeEvent(event: RuntimeEvent) {
  const payload = {
    ...event,
    path: event.path ?? window.location.pathname,
    timestamp: event.timestamp ?? new Date().toISOString(),
  };

  if (appConfig.logRuntimeEvents) {
    console.info('[runtime-monitoring]', payload);
  }

  if (!appConfig.runtimeMonitoringUrl) {
    return;
  }

  const body = JSON.stringify(payload);
  if (navigator.sendBeacon) {
    navigator.sendBeacon(appConfig.runtimeMonitoringUrl, body);
    return;
  }

  void fetch(appConfig.runtimeMonitoringUrl, {
    method: 'POST',
    keepalive: true,
    headers: { 'Content-Type': 'application/json' },
    body,
  });
}

export function reportRuntimeError(error: unknown, metadata?: Record<string, unknown>) {
  const message = error instanceof Error ? error.message : String(error);
  emitRuntimeEvent({
    type: 'frontend.error',
    message,
    metadata,
  });
}

export function reportNavigation(path: string) {
  emitRuntimeEvent({
    type: 'frontend.navigation',
    message: `Navigated to ${path}`,
    path,
  });
}

export function reportApiTiming(method: string, url: string, durationMs: number, statusCode?: number) {
  if (durationMs < appConfig.apiSlowRequestThresholdMs) {
    return;
  }

  emitRuntimeEvent({
    type: 'frontend.api_timing',
    message: `${method.toUpperCase()} ${url}`,
    durationMs,
    statusCode,
  });
}

export function setupRuntimeMonitoring() {
  if (initialized || typeof window === 'undefined') {
    return;
  }

  window.addEventListener('error', (event) => {
    reportRuntimeError(event.error ?? event.message, {
      source: event.filename,
      line: event.lineno,
      column: event.colno,
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    emitRuntimeEvent({
      type: 'frontend.promise_rejection',
      message: event.reason instanceof Error ? event.reason.message : String(event.reason),
    });
  });

  initialized = true;
}
