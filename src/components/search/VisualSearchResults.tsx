'use client'

import { motion } from 'framer-motion'
import { FiExternalLink, FiShoppingCart, FiHeart, FiTrendingUp } from 'react-icons/fi'
import { Product } from '@/services/productService'
import { formatCurrency } from '@/lib/utils'

interface VisualSearchResultsProps {
  results: Product[]
  loading?: boolean
  searchTime?: number
}

export default function VisualSearchResults({ 
  results, 
  loading = false,
  searchTime = 0 
}: VisualSearchResultsProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    )
  }

  if (!results || results.length === 0) {
    return (
      <div className="text-center py-20">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card p-12 rounded-3xl max-w-md mx-auto"
        >
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-2xl font-bold text-white mb-2 font-outfit">No Results Found</h3>
          <p className="text-slate-300">
            Try uploading a different image or adjusting your search criteria.
          </p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Results Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-3xl font-bold text-white font-outfit">
            Found {results.length} Similar Products
          </h2>
          {searchTime > 0 && (
            <p className="text-slate-400 mt-1">
              Search completed in {searchTime.toFixed(2)}s
            </p>
          )}
        </div>
      </motion.div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {results.map((product, index) => (
          <motion.div
            key={product.id || index}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="group"
          >
            <div className="glass-card rounded-2xl overflow-hidden hover:scale-105 transition-all duration-300 cursor-pointer h-full flex flex-col">
              {/* Product Image */}
              <div className="relative aspect-square bg-slate-800/50 overflow-hidden">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = 'https://via.placeholder.com/400x400?text=No+Image'
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-slate-500">
                    <FiShoppingCart className="w-20 h-20" />
                  </div>
                )}
                
                {/* Similarity Score Badge */}
                {(product as any).similarity && (
                  <div className="absolute top-3 right-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                    <FiTrendingUp className="w-3 h-3" />
                    {((product as any).similarity * 100).toFixed(0)}% Match
                  </div>
                )}

                {/* Quick Actions Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                  <button className="w-full bg-white/20 backdrop-blur-sm text-white py-2 rounded-lg font-medium hover:bg-white/30 transition-colors">
                    Quick View
                  </button>
                </div>
              </div>

              {/* Product Info */}
              <div className="p-4 flex-1 flex flex-col">
                {/* Category Badge */}
                {product.category && (
                  <span className="inline-block text-xs font-semibold text-blue-400 uppercase tracking-wide mb-2">
                    {product.category}
                  </span>
                )}

                {/* Product Name */}
                <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2 group-hover:text-blue-400 transition-colors font-outfit">
                  {product.name}
                </h3>

                {/* Brand */}
                {product.brand && (
                  <p className="text-sm text-slate-400 mb-2">
                    by {product.brand}
                  </p>
                )}

                {/* Description */}
                {product.description && (
                  <p className="text-sm text-slate-400 line-clamp-2 mb-3 flex-1">
                    {product.description}
                  </p>
                )}

                {/* Price & Platform */}
                <div className="flex items-center justify-between mt-auto pt-3 border-t border-slate-700/50">
                  <div>
                    {product.price ? (
                      <div className="text-2xl font-bold gradient-text font-outfit">
                        {formatCurrency(product.price, product.currency || 'INR')}
                      </div>
                    ) : (
                      <div className="text-sm text-slate-500">Price unavailable</div>
                    )}
                    {(product as any).platform && (
                      <div className="text-xs text-slate-500 mt-1">
                        {(product as any).platform}
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="w-9 h-9 rounded-lg bg-slate-800/50 flex items-center justify-center text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                    >
                      <FiHeart className="w-4 h-4" />
                    </motion.button>
                    
                    {product.url && (
                      <motion.a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className="w-9 h-9 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center text-white hover:shadow-lg hover:shadow-blue-500/50 transition-shadow"
                      >
                        <FiExternalLink className="w-4 h-4" />
                      </motion.a>
                    )}
                  </div>
                </div>

                {/* Rating */}
                {product.rating && (
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <span
                          key={i}
                          className={`text-sm ${
                            i < Math.floor(product.rating || 0)
                              ? 'text-yellow-400'
                              : 'text-slate-600'
                          }`}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                    {product.reviews_count && (
                      <span className="text-xs text-slate-500">
                        ({product.reviews_count})
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
