// Corrected import path to shared axios instance
// Previously './api' which does not exist in services directory caused module-not-found 500 errors
import api from '@/lib/api'
import { searchRateLimiter, uploadRateLimiter, sanitizeTextInput, validateSearchQuery, validateImageFile } from '@/lib/validators'
import { debounce } from '@/lib/utils'

export interface Product {
  id: string
  name: string
  description: string
  price: number
  currency: string
  image_url: string
  category: string
  brand?: string
  rating?: number
  reviews_count?: number
  url: string
}

export interface SearchResponse {
  results: Product[]
  total: number
  query: string
  search_time: number
}

export interface VisualSearchResponse {
  results: Product[]
  total: number
  search_time: number
}

/**
 * Text search for products
 */
export async function searchProducts(
  query: string,
  category?: string,
  limit: number = 20
): Promise<SearchResponse> {
  const response = await api.post('/api/search', {
    query,
    category,
    limit,
  })
  return response.data
}

/**
 * Semantic search using preprocessing engine (multilingual)
 * Uses the advanced 11-stage pipeline with intfloat/e5-base-v2 embeddings
 * Includes input validation, sanitization, and rate limiting
 */
export async function semanticSearch(
  query: string,
  top_k: number = 20,
  include_metadata: boolean = true
): Promise<SearchResponse> {
  // Validate query
  const validation = validateSearchQuery(query)
  if (!validation.isValid) {
    throw new Error(validation.error || 'Invalid search query')
  }

  // Check rate limit
  if (!searchRateLimiter.checkLimit()) {
    const resetTime = searchRateLimiter.getTimeUntilReset()
    throw new Error(`Rate limit exceeded. Please wait ${Math.ceil(resetTime / 1000)} seconds.`)
  }

  // Sanitize input
  const sanitizedQuery = sanitizeTextInput(query)

  const response = await api.post('/api/semantic-search', {
    query: sanitizedQuery,
    top_k,
    include_metadata,
  })
  
  return {
    results: response.data.products || [],
    total: response.data.count || 0,
    query: response.data.query_info?.original_query || sanitizedQuery,
    search_time: response.data.metrics?.total_latency_ms || 0,  // Use backend preprocessing time (accurate)
  }
}

/**
 * Visual search using image with CLIP
 * Includes file validation, size checks, and rate limiting
 */
export async function visualSearch(
  imageFile: File,
  category?: string,
  limit: number = 20
): Promise<VisualSearchResponse> {
  // Validate image file
  const validation = validateImageFile(imageFile)
  if (!validation.isValid) {
    throw new Error(validation.error || 'Invalid image file')
  }

  // Check rate limit
  if (!uploadRateLimiter.checkLimit()) {
    const resetTime = uploadRateLimiter.getTimeUntilReset()
    throw new Error(`Upload rate limit exceeded. Please wait ${Math.ceil(resetTime / 1000)} seconds.`)
  }

  const formData = new FormData()
  formData.append('file', imageFile)
  if (category) {
    // Sanitize category input
    formData.append('category', sanitizeTextInput(category))
  }
  formData.append('top_k', limit.toString())

  const response = await api.post('/api/visual/search_by_image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return {
    results: response.data.results || [],
    total: response.data.total_results || 0,
    search_time: response.data.search_time || 0,
  }
}

/**
 * Get product by ID
 */
export async function getProduct(id: string): Promise<Product> {
  const response = await api.get(`/api/products/${id}`)
  return response.data
}

/**
 * Get trending products
 */
export async function getTrendingProducts(limit: number = 10): Promise<Product[]> {
  const response = await api.get('/api/trending', {
    params: { limit },
  })
  return response.data
}

/**
 * Get product categories
 */
export async function getCategories(): Promise<string[]> {
  const response = await api.get('/api/categories')
  return response.data
}
