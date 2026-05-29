import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { reportRuntimeError } from '@/lib/runtime-monitoring';

interface ErrorBoundaryState {
  hasError: boolean;
  errorMessage: string;
}

export class ErrorBoundary extends React.Component<React.PropsWithChildren, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
    errorMessage: '',
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      errorMessage: error.message,
    };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    reportRuntimeError(error, { componentStack: info.componentStack });
  }

  private handleReset = () => {
    this.setState({ hasError: false, errorMessage: '' });
    window.location.assign(window.location.pathname);
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <Card className="max-w-lg w-full">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Something went wrong
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-600">
              The page hit an unexpected error. The event has been recorded so it can be investigated.
            </p>
            {this.state.errorMessage && (
              <pre className="text-xs bg-slate-100 rounded-md p-3 overflow-x-auto text-slate-700">
                {this.state.errorMessage}
              </pre>
            )}
            <Button onClick={this.handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reload page
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
}
