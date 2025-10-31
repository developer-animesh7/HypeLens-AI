'use client';

import { useState, useRef } from 'react';
import { ProductAnalysis } from '@/types/product';
import { ProductAnalyzer } from '@/components/ProductAnalyzer';
import { ProductResults } from '@/components/ProductResults';
import { ImageSearchUpload } from '@/components/ImageSearchUpload';
import { ImageSearchResults } from '@/components/ImageSearchResults';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ErrorMessage } from '@/components/ErrorMessage';

export default function Home() {
  const [analysis, setAnalysis] = useState<ProductAnalysis | null>(null);
  const [imageResults, setImageResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'url' | 'image'>('url');
  const [searchSource, setSearchSource] = useState<'auto' | 'local' | 'web'>('auto');
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleAnalyze = async (url: string) => {
    setLoading(true);
    setError(null);
    setAnalysis(null);
    setImageResults(null);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Failed to analyze product: ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
      
      // Scroll to results
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze product');
    } finally {
      setLoading(false);
    }
  };

  const handleImageResults = (results: any) => {
    setImageResults(results);
    setAnalysis(null);
    setError(null);
    
    // Scroll to results
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const clearResults = () => {
    setAnalysis(null);
    setImageResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-indigo-400/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Header with 3D effect */}
      <header className="bg-white/80 backdrop-blur-xl shadow-lg border-b border-white/20 sticky top-0 z-50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 group">
              <div className="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 text-white p-3 rounded-xl shadow-lg transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  HypeLens
                </h1>
                <p className="text-gray-600 text-sm">Smart product analysis & better alternatives</p>
              </div>
            </div>
            <div className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm font-semibold rounded-full shadow-lg animate-pulse">
              Powered by AI
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {/* Hero Section with animations */}
        <div className="text-center mb-12 animate-fade-in">
          <h2 className="text-5xl font-extrabold text-gray-900 mb-4 transform hover:scale-105 transition-transform duration-300">
            Find Better Products at
            <span className="block mt-2 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 animate-gradient">
              Lower Prices
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Our AI analyzes product quality and finds you better alternatives at lower prices. 
            Search by URL or upload an image to discover smarter shopping choices.
          </p>
        </div>

        {/* Search Tabs with 3D effect */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="flex bg-white/80 backdrop-blur-xl rounded-2xl p-2 shadow-xl border border-white/20">
            <button
              onClick={() => setActiveTab('url')}
              className={`flex-1 px-6 py-4 text-sm font-semibold rounded-xl transition-all duration-300 transform ${
                activeTab === 'url'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg scale-105'
                  : 'text-gray-600 hover:bg-gray-50 hover:scale-102'
              }`}
            >
              <span className="text-2xl mr-2">🔗</span>
              Search by URL
            </button>
            <button
              onClick={() => setActiveTab('image')}
              className={`flex-1 px-6 py-4 text-sm font-semibold rounded-xl transition-all duration-300 transform ${
                activeTab === 'image'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg scale-105'
                  : 'text-gray-600 hover:bg-gray-50 hover:scale-102'
              }`}
            >
              <span className="text-2xl mr-2">🖼️</span>
              Search by Image
            </button>
          </div>
        </div>

        {/* Search Interface with slide animation */}
        <div className="transition-all duration-500 ease-in-out">
          {activeTab === 'url' && (
            <div className="animate-slide-in">
              <ProductAnalyzer onAnalyze={handleAnalyze} disabled={loading} />
            </div>
          )}
          
          {activeTab === 'image' && (
            <div className="animate-slide-in">
              <div className="max-w-2xl mx-auto mb-6">
                <div className="bg-white/80 backdrop-blur-xl rounded-2xl p-6 shadow-xl border border-white/20">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-semibold text-gray-700 flex items-center space-x-2">
                      <span className="text-xl">🎯</span>
                      <span>Search Source:</span>
                    </label>
                    <select
                      className="border-2 border-gray-200 rounded-xl px-4 py-2 text-sm font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-300 bg-white/50 backdrop-blur"
                      value={searchSource}
                      onChange={e => setSearchSource(e.target.value as 'auto' | 'local' | 'web')}
                      title="Select search source"
                    >
                      <option value="auto">🔄 Auto (DB then Web)</option>
                      <option value="local">💾 Local (DB only)</option>
                      <option value="web">🌐 Web only</option>
                    </select>
                  </div>
                </div>
              </div>
              <ImageSearchUpload onResults={handleImageResults} disabled={loading} searchSource={searchSource} />
            </div>
          )}
        </div>

        {/* Loading State with 3D spinner */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-purple-600 rounded-full animate-spin" style={{animationDuration: '1.5s', animationDirection: 'reverse'}}></div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

        {/* Results */}
        <div ref={resultsRef} className="transition-all duration-500">
          {analysis && <ProductResults analysis={analysis} />}
          {imageResults ? (
            <ImageSearchResults results={imageResults} onClear={clearResults} />
          ) : (
            <></>
          )}
        </div>

        {/* Features Section with 3D cards */}
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="group relative bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20 transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Smart Analysis</h3>
              <p className="text-gray-600 text-center leading-relaxed">AI-powered analysis of product features, reviews, and specifications</p>
            </div>
          </div>
          
          <div className="group relative bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20 transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="bg-gradient-to-br from-green-500 to-green-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Better Prices</h3>
              <p className="text-gray-600 text-center leading-relaxed">Find alternatives that offer better value for money</p>
            </div>
          </div>
          
          <div className="group relative bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20 transform hover:-translate-y-2 hover:shadow-2xl transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="relative">
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Image Search</h3>
              <p className="text-gray-600 text-center leading-relaxed">Upload any product image to find similar items and better deals</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-xl border-t border-white/20 mt-20 relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p className="font-medium">&copy; 2025 HypeLens. Powered by advanced AI technology.</p>
          </div>
        </div>
      </footer>

      <style jsx global>{`
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }
        @keyframes slide-in {
          from { opacity: 0; transform: translateX(-20px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-slide-in {
          animation: slide-in 0.5s ease-out;
        }
        .scale-102 {
          transform: scale(1.02);
        }
      `}</style>
    </div>
  );
}
