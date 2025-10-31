'use client';

import { useState } from 'react';

interface ProductAnalyzerProps {
  onAnalyze: (url: string) => void;
  disabled?: boolean;
}

export function ProductAnalyzer({ onAnalyze, disabled = false }: ProductAnalyzerProps) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim() && !disabled) {
      onAnalyze(url.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !disabled) {
      handleSubmit(e);
    }
  };

  const setExampleUrl = (exampleUrl: string) => {
    setUrl(exampleUrl);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* URL Input */}
      <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border-2 border-white/20 p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex gap-3">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Paste product URL (Amazon, Flipkart, Myntra, etc.)"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                disabled={disabled}
              />
              <button
                type="submit"
                disabled={disabled || !url.trim()}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {disabled ? 'Analyzing...' : 'Analyze Product'}
              </button>
            </div>
          </form>

          {/* Example URLs */}
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-sm text-gray-600 mb-2">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setExampleUrl('https://www.amazon.in/dp/B08N5WRWNW')}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
                disabled={disabled}
              >
                Amazon Echo Dot
              </button>
              <button
                onClick={() => setExampleUrl('https://www.flipkart.com/samsung-galaxy-m32')}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
                disabled={disabled}
              >
                Samsung Phone
              </button>
              <button
                onClick={() => setExampleUrl('https://www.myntra.com/tshirts/nike')}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
                disabled={disabled}
              >
                Nike T-Shirt
              </button>
            </div>
          </div>
        </div>
    </div>
  );
}
