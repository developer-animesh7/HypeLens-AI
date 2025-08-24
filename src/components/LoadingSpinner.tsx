'use client';

export function LoadingSpinner() {
  return (
    <div className="flex justify-center py-12">
      <div className="bg-white rounded-lg shadow-sm border p-8 max-w-md w-full">
        <div className="text-center">
          {/* Animated Spinner */}
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200">
              <div className="rounded-full h-12 w-12 border-4 border-transparent border-t-blue-600"></div>
            </div>
          </div>
          
          {/* Loading Text */}
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Analyzing Product...
          </h3>
          
          {/* Loading Steps */}
          <div className="space-y-2 text-sm text-gray-600 mb-4">
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              <span>Extracting product information</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <span>Searching for alternatives</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-blue-300 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              <span>Calculating savings</span>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full animate-pulse"></div>
          </div>
          
          <p className="text-xs text-gray-500 mt-3">
            This may take a few seconds...
          </p>
        </div>
      </div>
    </div>
  );
}
