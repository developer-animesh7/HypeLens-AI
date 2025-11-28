'use client'

import { motion } from 'framer-motion'

interface LoadingSkeletonProps {
  count?: number
}

/**
 * Loading Skeleton Component
 * 
 * Displays skeleton screens while content is loading for better UX
 */
export function ProductCardSkeleton() {
  return (
    <div className="glass-card rounded-2xl overflow-hidden h-full animate-pulse">
      {/* Image Skeleton */}
      <div className="aspect-square bg-slate-800/50" />
      
      {/* Content Skeleton */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <div className="h-5 bg-slate-700/50 rounded w-3/4" />
        
        {/* Description */}
        <div className="space-y-2">
          <div className="h-4 bg-slate-700/30 rounded w-full" />
          <div className="h-4 bg-slate-700/30 rounded w-5/6" />
        </div>
        
        {/* Price */}
        <div className="h-6 bg-slate-700/50 rounded w-1/3" />
        
        {/* Buttons */}
        <div className="flex gap-2 pt-2">
          <div className="h-10 bg-slate-700/30 rounded flex-1" />
          <div className="h-10 bg-slate-700/30 rounded w-10" />
        </div>
      </div>
    </div>
  )
}

/**
 * Product Grid Loading Skeleton
 */
export function ProductGridSkeleton({ count = 8 }: LoadingSkeletonProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: index * 0.05 }}
        >
          <ProductCardSkeleton />
        </motion.div>
      ))}
    </div>
  )
}

/**
 * Search Results Skeleton
 */
export function SearchResultsSkeleton() {
  return (
    <div className="space-y-8">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between animate-pulse">
        <div className="space-y-2">
          <div className="h-8 bg-slate-700/50 rounded w-64" />
          <div className="h-4 bg-slate-700/30 rounded w-48" />
        </div>
      </div>

      {/* Grid Skeleton */}
      <ProductGridSkeleton count={12} />
    </div>
  )
}

/**
 * Inline Loading Spinner
 */
export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-16 h-16 border-4',
  }

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      className={`${sizeClasses[size]} border-blue-500 border-t-transparent rounded-full`}
    />
  )
}
