'use client';

import { useState } from 'react';

interface ImageSearchResultsProps {
  results: any;
  onClear: () => void;
}

export function ImageSearchResults({ results, onClear }: ImageSearchResultsProps) {
  if (!results) {
    return null;
  }

  if (results.status === 'error') {
    return (
      <div className="max-w-7xl mx-auto mt-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-red-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-red-800">Search Failed</h3>
                <p className="text-red-700 text-sm">{results.error || 'Unable to process the image. Please try again.'}</p>
              </div>
            </div>
            <button onClick={onClear} className="text-red-600 hover:text-red-800 text-sm">Dismiss</button>
          </div>
        </div>
      </div>
    );
  }

  if (results.status !== 'success' || !results.results || results.results.length === 0) {
    return (
      <div className="max-w-7xl mx-auto mt-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-yellow-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.289-5.5-3.109" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-yellow-800">No Similar Products Found</h3>
                <p className="text-yellow-700 text-sm">Try a different image or adjust the similarity threshold.</p>
              </div>
            </div>
            <button onClick={onClear} className="text-yellow-700 hover:text-yellow-900 text-sm">Clear</button>
          </div>
      </div>
    </div>
    );
  }

  // PHASE 3: Use new API format (exact_match + similar_items)
  const exactMatch = results.exact_match;
  const similarItems = results.similar_items || [];
  
  // Fallback to old format if new format not available
  const hasExactMatch = exactMatch !== null && exactMatch !== undefined;
  const hasSimilarItems = similarItems.length > 0;
  
  return (
    <div className="max-w-7xl mx-auto mt-8 animate-fade-in-up">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
          Search Results ({results.total_results || 0})
        </h2>
        <button
          onClick={onClear}
          className="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800 bg-white/80 backdrop-blur rounded-xl border-2 border-gray-200 hover:border-gray-300 transition-all duration-300 transform hover:scale-105 shadow-lg"
        >
          ✕ Clear results
        </button>
      </div>
      
      {/* EXACT MATCH Section - PHASE 3: With Multi-Store Pricing */}
      {hasExactMatch && (
        <div className="mb-10 animate-scale-in">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-3 rounded-2xl font-bold text-lg shadow-2xl transform hover:scale-105 transition-all duration-300 animate-pulse-slow">
              ✓ EXACT MATCH
            </div>
            <span className="text-gray-500 text-sm font-medium">Perfect match found!</span>
          </div>
          <ExactMatchCard product={exactMatch} />
        </div>
      )}
      
      {/* SIMILAR ITEMS Section */}
      {hasSimilarItems && (
        <div className="animate-fade-in-up">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-2xl font-bold text-lg shadow-2xl transform hover:scale-105 transition-all duration-300">
              ≈ SIMILAR ITEMS
            </div>
            <span className="text-gray-500 text-sm font-medium">({similarItems.length} product{similarItems.length > 1 ? 's' : ''})</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {similarItems.map((product: any, index: number) => (
              <ProductCard key={`similar-${index}`} product={product} index={index} isExactMatch={false} />
            ))}
          </div>
        </div>
      )}
      
      {!hasExactMatch && !hasSimilarItems && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No products found matching your search.</p>
        </div>
      )}

      <style jsx>{`
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.6s ease-out;
        }
        @keyframes scale-in {
          from {
            opacity: 0;
            transform: scale(0.9);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-scale-in {
          animation: scale-in 0.5s ease-out;
        }
        @keyframes pulse-slow {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.02);
          }
        }
        .animate-pulse-slow {
          animation: pulse-slow 2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}

// PHASE 3: ExactMatchCard with Multi-Store Pricing
function ExactMatchCard({ product }: { product: any }) {
  const [selectedStore, setSelectedStore] = useState(0);
  
  // Extract listings (multi-store pricing)
  const listings = product.listings || [];
  const hasListings = listings.length > 0;
  
  // Sort listings by price (cheapest first)
  const sortedListings = hasListings 
    ? [...listings].sort((a, b) => (a.price || 0) - (b.price || 0))
    : [];
  
  const cheapestListing = sortedListings[0];
  const currentListing = sortedListings[selectedStore] || cheapestListing;
  
  return (
    <div className="group relative bg-gradient-to-br from-green-50 via-emerald-50 to-green-50 rounded-3xl shadow-2xl border-4 border-green-400 overflow-hidden transform transition-all duration-500 hover:shadow-3xl hover:-translate-y-2">
      {/* Animated background glow */}
      <div className="absolute inset-0 bg-gradient-to-r from-green-400/20 to-emerald-400/20 blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-500"></div>
      
      {/* Exact Match Banner */}
      <div className="relative bg-gradient-to-r from-green-500 via-emerald-600 to-green-500 text-white py-4 px-6 shadow-xl animate-gradient-x">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-white text-green-600 rounded-full w-12 h-12 flex items-center justify-center animate-bounce-slow">
              <span className="text-3xl">✓</span>
            </div>
            <div>
              <h3 className="text-xl font-bold drop-shadow-lg">Perfect Match Found!</h3>
              <p className="text-sm text-green-100">
                {product.similarity_score ? `${(product.similarity_score * 100).toFixed(0)}% Match` : 'Exact Match'} • 
                {hasListings ? ` Available at ${sortedListings.length} store${sortedListings.length > 1 ? 's' : ''}` : ' Available'}
              </p>
            </div>
          </div>
          {product.similarity_score && (
            <div className="bg-white text-green-600 px-6 py-3 rounded-2xl text-xl font-extrabold shadow-2xl transform group-hover:scale-110 transition-all duration-300">
              {(product.similarity_score * 100).toFixed(0)}%
            </div>
          )}
        </div>
      </div>
      
      <div className="relative grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
        {/* Left: Product Info */}
        <div className="space-y-6">
          {/* Product Image */}
          {product.image_url && (
            <div className="relative group/img aspect-w-16 aspect-h-9 bg-white rounded-2xl overflow-hidden shadow-xl border-4 border-white transform transition-all duration-500 hover:scale-105">
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-72 object-cover transform transition-transform duration-700 group-hover/img:scale-110"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = 'https://via.placeholder.com/400x300?text=Product+Image';
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover/img:opacity-100 transition-opacity duration-500"></div>
            </div>
          )}
          
          {/* Product Name */}
          <h3 className="font-extrabold text-gray-900 text-2xl leading-tight">
            {product.name}
          </h3>
          
          {/* Category */}
          {product.category && (
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border-2 border-green-300 shadow-lg">
                📦 {product.category}
              </span>
            </div>
          )}
          
          {/* Description */}
          {product.description && (
            <p className="text-base text-gray-700 leading-relaxed">
              {product.description}
            </p>
          )}
          
          {/* AI Scores */}
          {(product.clip_score || product.keyword_score) && (
            <div className="bg-white rounded-2xl p-6 space-y-3 shadow-xl border-2 border-green-200">
              <h4 className="text-xs font-extrabold text-gray-600 uppercase tracking-wider mb-3 flex items-center">
                <span className="mr-2">🤖</span> AI Match Scores
              </h4>
              {product.clip_score && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700 font-semibold">🖼️ Visual Match:</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-emerald-500 h-full rounded-full transition-all duration-1000"
                        style={{width: `${product.clip_score * 100}%`}}
                      ></div>
                    </div>
                    <span className="font-extrabold text-green-700 min-w-[50px]">{(product.clip_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              )}
              {product.keyword_score && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700 font-semibold">📝 Text Match:</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-emerald-500 h-full rounded-full transition-all duration-1000"
                        style={{width: `${product.keyword_score * 100}%`}}
                      ></div>
                    </div>
                    <span className="font-extrabold text-green-700 min-w-[50px]">{(product.keyword_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Right: Multi-Store Pricing */}
        <div className="space-y-6">
          <h4 className="text-2xl font-extrabold text-gray-900 flex items-center">
            <span className="text-3xl mr-3">🏪</span>
            {hasListings ? 'Compare Prices Across Stores' : 'Price Information'}
          </h4>
          
          {hasListings ? (
            <>
              {/* Store Selection Tabs */}
              <div className="flex flex-wrap gap-3">
                {sortedListings.map((listing: any, index: number) => {
                  const isCheapest = index === 0;
                  const isSelected = selectedStore === index;
                  return (
                    <button
                      key={index}
                      onClick={() => setSelectedStore(index)}
                      className={`px-5 py-3 rounded-xl font-bold text-sm transition-all duration-300 transform ${
                        isSelected
                          ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-2xl scale-110'
                          : 'bg-white text-gray-700 border-2 border-gray-300 hover:border-green-400 hover:scale-105 shadow-lg'
                      }`}
                    >
                      {listing.store_name || 'Store'}
                      {isCheapest && (
                        <span className="ml-2 text-base">💰</span>
                      )}
                    </button>
                  );
                })}
              </div>
              
              {/* Selected Store Details */}
              <div className="bg-white rounded-2xl p-8 shadow-2xl border-4 border-green-200 transform transition-all duration-500 hover:shadow-3xl">
                <div className="mb-6">
                  <p className="text-sm text-gray-500 mb-2 font-semibold">Current Price at {currentListing.store_name}</p>
                  <div className="flex items-baseline space-x-3">
                    <span className="text-5xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                      ₹{currentListing.price?.toLocaleString('en-IN')}
                    </span>
                    {currentListing.original_price && currentListing.original_price > currentListing.price && (
                      <span className="text-xl text-gray-400 line-through">
                        ₹{currentListing.original_price?.toLocaleString('en-IN')}
                      </span>
                    )}
                  </div>
                  {currentListing.original_price && currentListing.original_price > currentListing.price && (
                    <p className="text-sm text-green-600 font-extrabold mt-2 flex items-center space-x-2">
                      <span className="text-xl">🎉</span>
                      <span>Save ₹{(currentListing.original_price - currentListing.price).toLocaleString('en-IN')} (
                      {(((currentListing.original_price - currentListing.price) / currentListing.original_price) * 100).toFixed(0)}% off)</span>
                    </p>
                  )}
                </div>
                
                {currentListing.in_stock !== undefined && (
                  <div className="mb-4">
                    <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-extrabold shadow-lg ${
                      currentListing.in_stock 
                        ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' 
                        : 'bg-gradient-to-r from-red-500 to-red-600 text-white'
                    }`}>
                      {currentListing.in_stock ? '✓ In Stock' : '✗ Out of Stock'}
                    </span>
                  </div>
                )}
                
                {currentListing.seller_name && (
                  <p className="text-sm text-gray-600 mb-6">
                    Sold by: <span className="font-bold text-gray-900">{currentListing.seller_name}</span>
                  </p>
                )}
                
                {currentListing.product_url && (
                  <a
                    href={currentListing.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full bg-gradient-to-r from-orange-500 via-red-600 to-orange-500 hover:from-orange-600 hover:via-red-700 hover:to-orange-600 text-white text-center py-5 px-6 rounded-2xl font-extrabold text-lg shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105 animate-gradient-x"
                  >
                    🛒 Buy on {currentListing.store_name}
                  </a>
                )}
              </div>
              
              {/* Price Comparison Table */}
              {sortedListings.length > 1 && (
                <div className="bg-white rounded-2xl p-6 shadow-xl border-2 border-green-200">
                  <h5 className="text-base font-extrabold text-gray-800 mb-4 flex items-center">
                    <span className="text-xl mr-2">💰</span> Price Comparison
                  </h5>
                  <div className="space-y-3">
                    {sortedListings.map((listing: any, index: number) => (
                      <div 
                        key={index}
                        className={`flex items-center justify-between p-4 rounded-xl transition-all duration-300 ${
                          index === 0 ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 shadow-lg transform scale-105' : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <span className="text-base font-extrabold text-gray-800">
                            {listing.store_name}
                          </span>
                          {index === 0 && (
                            <span className="text-xs bg-gradient-to-r from-green-500 to-emerald-500 text-white px-3 py-1 rounded-full font-bold shadow-lg animate-pulse">
                              Cheapest
                            </span>
                          )}
                        </div>
                        <span className="text-base font-black text-gray-900">
                          ₹{listing.price?.toLocaleString('en-IN')}
                        </span>
                      </div>
                    ))}
                  </div>
                  {sortedListings.length > 1 && cheapestListing && (
                    <p className="text-xs text-gray-600 mt-4 flex items-center space-x-2">
                      <span className="text-base">💡</span>
                      <span>You can save up to ₹{(
                        Math.max(...sortedListings.map((l: any) => l.price || 0)) - (cheapestListing.price || 0)
                      ).toLocaleString('en-IN')} by choosing the cheapest option</span>
                    </p>
                  )}
                </div>
              )}
            </>
          ) : (
            // Fallback: Single price (backward compatibility)
            <div className="bg-white rounded-2xl p-8 shadow-2xl border-4 border-green-200">
              <p className="text-sm text-gray-500 mb-3 font-semibold">Price</p>
              <div className="text-5xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-6">
                ₹{product.price?.toLocaleString('en-IN')}
              </div>
              {product.url && (
                <a
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full bg-gradient-to-r from-orange-500 via-red-600 to-orange-500 hover:from-orange-600 hover:via-red-700 hover:to-orange-600 text-white text-center py-5 px-6 rounded-2xl font-extrabold text-lg shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105"
                >
                  🛒 Buy on {product.platform || 'Flipkart'}
                </a>
              )}
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        @keyframes gradient-x {
          0%, 100% {
            background-size: 200% 200%;
            background-position: 0% 50%;
          }
          50% {
            background-size: 200% 200%;
            background-position: 100% 50%;
          }
        }
        .animate-gradient-x {
          animation: gradient-x 3s ease infinite;
        }
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-5px);
          }
        }
        .animate-bounce-slow {
          animation: bounce-slow 2s ease-in-out infinite;
        }
        .shadow-3xl {
          box-shadow: 0 35px 60px -15px rgba(0, 0, 0, 0.3);
        }
      `}</style>
    </div>
  );
}

// Separate ProductCard component with 3D effects
function ProductCard({ product, index, isExactMatch }: { product: any; index: number; isExactMatch: boolean }) {
  return (
    <div className={`group relative bg-white rounded-2xl shadow-xl border-3 overflow-hidden transition-all duration-500 transform hover:-translate-y-4 hover:shadow-3xl hover:scale-105 ${isExactMatch ? 'border-green-400' : 'border-gray-200'} animate-card-in`}
      style={{animationDelay: `${index * 0.1}s`}}>
      
      {/* Hover glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      {/* Match Score Badge */}
      <div className="absolute top-4 right-4 z-10">
        <div className={`${isExactMatch ? 'bg-gradient-to-r from-green-500 to-emerald-600 ring-4 ring-green-300' : 'bg-gradient-to-r from-blue-500 to-purple-600'} text-white px-4 py-2 rounded-full text-sm font-extrabold shadow-2xl transform group-hover:scale-110 transition-all duration-300`}>
          {product.similarity_score ? `${(product.similarity_score * 100).toFixed(0)}% Match` : 'Match'}
        </div>
      </div>
      
      {isExactMatch && (
        <div className="absolute top-4 left-4 z-10">
          <div className="bg-green-500 text-white px-3 py-2 rounded-full text-sm font-extrabold shadow-2xl animate-pulse">
            ✓ EXACT
          </div>
        </div>
      )}
      
      {/* Product Image with 3D hover */}
      {product.image_url && (
        <div className="relative aspect-w-16 aspect-h-9 bg-gradient-to-br from-gray-100 to-gray-50 overflow-hidden">
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-64 object-cover transform transition-transform duration-700 group-hover:scale-125 group-hover:rotate-2"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = 'https://via.placeholder.com/400x300?text=Product+Image';
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        </div>
      )}
      
      <div className="relative p-6 space-y-4">
        {/* Product Name */}
        <h3 className="font-extrabold text-gray-900 text-lg leading-tight line-clamp-2 group-hover:text-blue-600 transition-colors duration-300">
          {product.name}
        </h3>
        
        {/* Price and Platform */}
        <div className="flex items-center justify-between">
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              ₹{product.price?.toLocaleString('en-IN')}
            </span>
          </div>
          <span className="text-xs font-extrabold text-white bg-gradient-to-r from-blue-500 to-purple-600 px-3 py-2 rounded-full shadow-lg">
            {product.platform || 'Flipkart'}
          </span>
        </div>
        
        {/* Category Tag */}
        {product.category && (
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-3 py-2 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border-2 border-blue-200 shadow-md">
              📦 {product.category}
            </span>
          </div>
        )}
        
        {/* Description */}
        {product.description && (
          <p className="text-sm text-gray-600 line-clamp-3 leading-relaxed">
            {product.description}
          </p>
        )}
        
        {/* AI Scores with progress bars */}
        {(product.clip_score || product.keyword_score) && (
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 space-y-3">
            {product.clip_score && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-600 font-bold">🖼️ Visual Match:</span>
                  <span className="font-extrabold text-blue-700">{(product.clip_score * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full transition-all duration-1000"
                    style={{width: `${product.clip_score * 100}%`}}
                  ></div>
                </div>
              </div>
            )}
            {product.keyword_score && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-600 font-bold">📝 Text Match:</span>
                  <span className="font-extrabold text-purple-700">{(product.keyword_score * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full transition-all duration-1000"
                    style={{width: `${product.keyword_score * 100}%`}}
                  ></div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Action Buttons */}
        <div className="flex space-x-2 pt-2">
          {product.url && (
            <a
              href={product.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white text-center py-4 px-4 rounded-xl font-extrabold text-sm shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-2"
            >
              <span>🛒</span>
              <span>Buy Now</span>
            </a>
          )}
          <button
            onClick={() => {
              const text = `${product.name}\n₹${product.price?.toLocaleString('en-IN')} on ${product.platform}\n${product.url}`;
              navigator.clipboard.writeText(text);
              const btn = document.getElementById(`copy-btn-${index}`);
              if (btn) {
                btn.textContent = '✓';
                setTimeout(() => btn.textContent = '📋', 2000);
              }
            }}
            id={`copy-btn-${index}`}
            className="px-5 py-4 border-3 border-gray-300 rounded-xl hover:bg-gray-100 hover:border-gray-400 transition-all duration-300 text-xl transform hover:scale-110 shadow-lg"
            title="Copy product info"
          >
            📋
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes card-in {
          from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
        .animate-card-in {
          animation: card-in 0.6s ease-out forwards;
          opacity: 0;
        }
        .border-3 {
          border-width: 3px;
        }
        .shadow-3xl {
          box-shadow: 0 35px 60px -15px rgba(0, 0, 0, 0.3);
        }
      `}</style>
    </div>
  );
}

