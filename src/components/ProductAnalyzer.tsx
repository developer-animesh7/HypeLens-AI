'use client';

import { useState } from 'react';

interface ProductAnalyzerProps {
  onAnalyze: (url: string) => void;
  disabled?: boolean;
}

export function ProductAnalyzer({ onAnalyze, disabled = false }: ProductAnalyzerProps) {
  const [url, setUrl] = useState('');
  const [activeTab, setActiveTab] = useState<'url' | 'image'>('url');

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
      {/* Tab Navigation */}
      <div className="flex justify-center mb-6">
        <div className="bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('url')}
            className={`px-4 py-2 rounded-md transition-all ${
              activeTab === 'url'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Product URL
          </button>
          <button
            onClick={() => setActiveTab('image')}
            className={`px-4 py-2 rounded-md transition-all ${
              activeTab === 'image'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Upload Image
          </button>
        </div>
      </div>

      {/* URL Input */}
      {activeTab === 'url' && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
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
      )}

      {/* Image Upload */}
      {activeTab === 'image' && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
            <div className="text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    Drop product image here or click to upload
                  </span>
                  <input id="file-upload" name="file-upload" type="file" className="sr-only" accept="image/*" disabled={disabled} />
                </label>
                <p className="mt-2 text-xs text-gray-500">PNG, JPG, JPEG up to 10MB</p>
              </div>
              <div className="mt-4">
                <button
                  type="button"
                  disabled={disabled}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  Choose File
                </button>
              </div>
            </div>
          </div>
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-500">
              Upload a product image and our AI will identify and analyze it for you.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
