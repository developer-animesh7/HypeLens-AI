'use client';

import { ProductAnalysis } from '@/types/product';
import { ProductCard } from './ProductCard';

interface ProductResultsProps {
  analysis: ProductAnalysis;
}

export function ProductResults({ analysis }: ProductResultsProps) {
  const { original_product, alternatives, savings_summary } = analysis;

  return (
    <div className="mt-12 space-y-8">
      {/* Results Header */}
      <div className="text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Analysis Results</h3>
        <p className="text-gray-600">
          Found {alternatives.length} better alternatives that could save you money
        </p>
      </div>

      {/* Original Product */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full mr-3">
            Original
          </span>
          Your Selected Product
        </h4>
        <ProductCard product={original_product} isOriginal={true} />
      </div>

      {/* Alternatives */}
      {alternatives.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full mr-3">
              Alternatives
            </span>
            Better Options Found
          </h4>
          <div className="grid gap-4">
            {alternatives.map((product, index) => (
              <ProductCard 
                key={index} 
                product={product} 
                isOriginal={false}
                savings={original_product.price - product.price}
              />
            ))}
          </div>
        </div>
      )}

      {/* Savings Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-gray-800 flex items-center">
            <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            Potential Savings
          </h4>
          <div className="text-right">
            <div className="text-2xl font-bold text-green-600">
              ₹{savings_summary.total_savings.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">
              Up to {savings_summary.average_savings_percentage.toFixed(1)}% savings
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4">
            <h5 className="font-medium text-gray-800 mb-2">Price Comparison</h5>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Original Price:</span>
                <span className="font-medium">₹{savings_summary.price_comparison.original_price.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Best Alternative:</span>
                <span className="font-medium text-green-600">₹{savings_summary.price_comparison.lowest_alternative_price.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Average Alternative:</span>
                <span className="font-medium">₹{savings_summary.price_comparison.average_alternative_price.toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <h5 className="font-medium text-gray-800 mb-2">Best Alternative</h5>
            <div className="space-y-2">
              <div className="font-medium text-sm truncate">{savings_summary.best_alternative.name}</div>
              <div className="text-sm text-gray-600">
                Price: ₹{savings_summary.best_alternative.price.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">
                Platform: {savings_summary.best_alternative.platform || 'N/A'}
              </div>
              {savings_summary.best_alternative.rating && (
                <div className="flex items-center text-sm">
                  <span className="text-yellow-400">★</span>
                  <span className="ml-1 text-gray-600">
                    {savings_summary.best_alternative.rating} 
                    {savings_summary.best_alternative.reviews_count && 
                      ` (${savings_summary.best_alternative.reviews_count} reviews)`
                    }
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 text-center">
            <svg className="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Our AI evaluates specifications, reviews, and features to ensure alternatives match or exceed quality.
          </p>
        </div>
      </div>
    </div>
  );
}
