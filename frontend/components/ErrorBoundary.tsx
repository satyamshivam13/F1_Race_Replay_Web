'use client';

import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error Boundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-f1-gray-800 flex items-center justify-center p-4">
          <div className="f1-card max-w-2xl w-full p-8 text-center animate-scale-in">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-500/20 mb-4">
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
            
            <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
            <p className="text-gray-400 mb-6">
              We encountered an unexpected error. Please try refreshing the page.
            </p>
            
            {this.state.error && (
              <details className="text-left bg-f1-gray-600 rounded p-4 mb-6">
                <summary className="cursor-pointer text-sm font-mono text-gray-400 mb-2">
                  Error details
                </summary>
                <pre className="text-xs overflow-auto text-red-400">
                  {this.state.error.toString()}
                  {this.state.error.stack}
                </pre>
              </details>
            )}
            
            <button
              onClick={() => window.location.reload()}
              className="f1-button"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
