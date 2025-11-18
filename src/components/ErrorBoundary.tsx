'use client'

import React, { Component, ReactNode } from 'react'
import { FiAlertCircle, FiRefreshCw, FiHome } from 'react-icons/fi'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

/**
 * Error Boundary Component
 * 
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 */
export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error Boundary caught an error:', error, errorInfo)
    }

    // Log to monitoring service in production
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send to monitoring service (Sentry, LogRocket, etc.)
      this.logErrorToService(error, errorInfo)
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    this.setState({
      error,
      errorInfo,
    })
  }

  logErrorToService(error: Error, errorInfo: React.ErrorInfo) {
    // TODO: Implement error logging to your monitoring service
    // Example: Sentry.captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } })
    console.error('Production Error:', {
      error: error.toString(),
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
          <div className="glass-card p-8 md:p-12 rounded-3xl max-w-2xl w-full">
            <div className="text-center space-y-6">
              {/* Error Icon */}
              <div className="flex justify-center">
                <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center">
                  <FiAlertCircle className="w-10 h-10 text-red-400" />
                </div>
              </div>

              {/* Error Title */}
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-white mb-3 font-outfit">
                  Oops! Something went wrong
                </h1>
                <p className="text-lg text-slate-300">
                  We encountered an unexpected error. Don't worry, we're on it!
                </p>
              </div>

              {/* Error Details (Development Only) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="bg-slate-900/50 rounded-xl p-4 text-left">
                  <p className="text-sm font-mono text-red-400 mb-2">
                    {this.state.error.toString()}
                  </p>
                  {this.state.errorInfo && (
                    <details className="text-xs text-slate-400 font-mono">
                      <summary className="cursor-pointer hover:text-slate-300">
                        Component Stack
                      </summary>
                      <pre className="mt-2 overflow-auto max-h-40">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={this.handleReset}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:scale-105 transition-all flex items-center justify-center gap-2"
                >
                  <FiRefreshCw className="w-5 h-5" />
                  Try Again
                </button>
                <a
                  href="/"
                  className="px-6 py-3 bg-slate-800 text-white rounded-xl font-medium hover:bg-slate-700 transition-all flex items-center justify-center gap-2"
                >
                  <FiHome className="w-5 h-5" />
                  Go Home
                </a>
              </div>

              {/* Help Text */}
              <p className="text-sm text-slate-400">
                If this problem persists, please contact support.
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
