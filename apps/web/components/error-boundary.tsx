"use client";

import React from "react";

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950">
          <div className="bg-slate-900 rounded-lg border border-red-800 p-8 max-w-md mx-4 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-8 h-8 rounded-full bg-red-900 flex items-center justify-center text-red-400 font-bold">
                !
              </span>
              <h2 className="text-lg font-semibold text-slate-100">
                Something went wrong
              </h2>
            </div>
            <p className="text-sm text-slate-600 mb-4">
              An unexpected error occurred while rendering this page. Try
              refreshing or navigating to another page.
            </p>
            {this.state.error && (
              <pre className="bg-slate-950 rounded p-3 text-xs text-red-400 mb-4 overflow-auto max-h-32">
                {this.state.error.message}
              </pre>
            )}
            <div className="flex gap-2">
              <button
                onClick={() => window.location.reload()}
                className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-500 transition-colors"
              >
                Reload Page
              </button>
              <button
                onClick={() => this.setState({ hasError: false, error: null })}
                className="text-sm text-slate-600 px-4 py-2 rounded hover:bg-slate-800 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
