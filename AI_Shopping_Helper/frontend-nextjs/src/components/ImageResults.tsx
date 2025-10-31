'use client';

interface Product {
  product_id: number;
  name: string;
  category: string;
  price: number;
  platform: string;
  affiliate_link: string;
  image_url: string;
  description: string;
  specs: string;
}

interface ImageResultsProps {
  results: {
    status: string;
    total_results: number;
    results: Product[];
  };
  loading?: boolean;
}

export function ImageResults({ results, loading = false }: ImageResultsProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <div>
            <h3 className="text-lg font-medium text-gray-900">Searching for similar products...</h3>
            <p className="text-gray-600">Using AI visual search to find matches</p>
          </div>
        </div>
      </div>
    );
  }

  if (results.status === 'error') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <div className="text-red-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-medium text-red-800">Search Failed</h3>
            <p className="text-red-600">Unable to process image. Please try again with a different image.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!results.results || results.results.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <div className="text-yellow-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.289-5.5-3.109" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-medium text-yellow-800">No Similar Products Found</h3>
            <p className="text-yellow-600">Try uploading a different image or check back later for more products.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-6 py-4 border-b">
        <h3 className="text-lg font-semibold text-gray-900">
          🎯 Found {results.total_results} Similar Products
        </h3>
        <p className="text-gray-600 text-sm">
          AI-powered visual search results, sorted by price
        </p>
      </div>

      <div className="p-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {results.results.map((product) => (
            <div
              key={product.product_id}
              className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Product Image */}
              <div className="aspect-square bg-gray-100 relative">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = '/api/placeholder/300/300';
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}
                
                {/* Platform Badge */}
                <div className="absolute top-2 left-2">
                  <span className="bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                    {product.platform}
                  </span>
                </div>
              </div>

              {/* Product Details */}
              <div className="p-4 space-y-3">
                <div>
                  <h4 className="font-medium text-gray-900 line-clamp-2 text-sm">
                    {product.name}
                  </h4>
                  <p className="text-xs text-gray-500 mt-1">
                    {product.category}
                  </p>
                </div>

                {/* Price */}
                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold text-green-600">
                    ₹{product.price?.toLocaleString('en-IN') || 'N/A'}
                  </span>
                  <span className="text-xs text-gray-500">
                    ID: {product.product_id}
                  </span>
                </div>

                {/* Description */}
                {product.description && (
                  <p className="text-xs text-gray-600 line-clamp-2">
                    {product.description}
                  </p>
                )}

                {/* Action Button */}
                <a
                  href={product.affiliate_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded text-sm font-medium transition-colors"
                >
                  View Product →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-6 py-3 border-t">
        <p className="text-xs text-gray-500 text-center">
          Results powered by CLIP ViT-B/32 visual similarity search
        </p>
      </div>
    </div>
  );
}
