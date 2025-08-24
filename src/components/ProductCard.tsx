'use client';

import { Product } from '@/types/product';

interface ProductCardProps {
  product: Product;
  isOriginal?: boolean;
  savings?: number;
}

export function ProductCard({ product, isOriginal = false, savings }: ProductCardProps) {
  const formatPrice = (price: number) => `₹${price.toLocaleString()}`;
  
  const openProductUrl = () => {
    if (product.url) {
      window.open(product.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${isOriginal ? 'border-blue-200 bg-blue-50' : 'border-green-200 bg-green-50'} hover:shadow-md transition-shadow`}>
      <div className="flex flex-col md:flex-row gap-4">
        {/* Product Image */}
        <div className="md:w-32 md:h-32 w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
          {product.image_url ? (
            <img 
              src={product.image_url} 
              alt={product.name}
              className="w-full h-full object-cover rounded-lg"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                target.nextElementSibling?.classList.remove('hidden');
              }}
            />
          ) : null}
          <div className={`flex items-center justify-center text-gray-400 ${product.image_url ? 'hidden' : ''}`}>
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        {/* Product Details */}
        <div className="flex-1">
          <div className="flex justify-between items-start mb-2">
            <h5 className="font-semibold text-gray-800 line-clamp-2 text-sm md:text-base">
              {product.name}
            </h5>
            {savings && savings > 0 && (
              <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full ml-2 flex-shrink-0">
                Save ₹{savings.toLocaleString()}
              </span>
            )}
          </div>

          <div className="space-y-2">
            {/* Price */}
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-gray-900">
                {formatPrice(product.price)}
              </span>
              {product.platform && (
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {product.platform}
                </span>
              )}
            </div>

            {/* Rating */}
            {product.rating && (
              <div className="flex items-center gap-1">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className={`w-4 h-4 ${i < Math.floor(product.rating!) ? 'text-yellow-400' : 'text-gray-300'}`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <span className="text-sm text-gray-600">
                  {product.rating.toFixed(1)}
                  {product.reviews_count && ` (${product.reviews_count})`}
                </span>
              </div>
            )}

            {/* Brand */}
            {product.brand && (
              <div className="text-sm text-gray-600">
                Brand: <span className="font-medium">{product.brand}</span>
              </div>
            )}

            {/* Availability */}
            {product.availability && (
              <div className="text-sm">
                <span className={`${product.availability.toLowerCase().includes('stock') ? 'text-green-600' : 'text-orange-600'}`}>
                  {product.availability}
                </span>
              </div>
            )}

            {/* Quality Scores */}
            {(product.quality_score || product.value_score || product.overall_score) && (
              <div className="flex gap-4 text-xs">
                {product.quality_score && (
                  <div className="flex items-center gap-1">
                    <span className="text-gray-500">Quality:</span>
                    <span className="font-medium">{product.quality_score}/10</span>
                  </div>
                )}
                {product.value_score && (
                  <div className="flex items-center gap-1">
                    <span className="text-gray-500">Value:</span>
                    <span className="font-medium">{product.value_score}/10</span>
                  </div>
                )}
                {product.overall_score && (
                  <div className="flex items-center gap-1">
                    <span className="text-gray-500">Overall:</span>
                    <span className="font-medium">{product.overall_score}/10</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Action Button */}
          <div className="mt-3 pt-3 border-t border-gray-200">
            <button
              onClick={openProductUrl}
              disabled={!product.url}
              className={`w-full px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isOriginal
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-green-600 text-white hover:bg-green-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isOriginal ? 'View Original Product' : 'View Alternative'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
