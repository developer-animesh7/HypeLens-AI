/**
 * Input Validation and Sanitization Utilities
 * 
 * Provides functions to validate and sanitize user inputs to prevent XSS,
 * injection attacks, and other security vulnerabilities.
 */

// ============================================================================
// CONSTANTS
// ============================================================================

const MAX_SEARCH_QUERY_LENGTH = 500
const MIN_SEARCH_QUERY_LENGTH = 1
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
const ALLOWED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.webp']

// ============================================================================
// TEXT INPUT VALIDATION
// ============================================================================

/**
 * Validates search query text
 * 
 * @param query - The search query to validate
 * @returns Validation result with error message if invalid
 */
export interface ValidationResult {
  isValid: boolean
  error?: string
}

export function validateSearchQuery(query: string): ValidationResult {
  // Check if empty
  if (!query || query.trim().length === 0) {
    return {
      isValid: false,
      error: 'Search query cannot be empty',
    }
  }

  // Check length
  if (query.length < MIN_SEARCH_QUERY_LENGTH) {
    return {
      isValid: false,
      error: `Search query must be at least ${MIN_SEARCH_QUERY_LENGTH} character`,
    }
  }

  if (query.length > MAX_SEARCH_QUERY_LENGTH) {
    return {
      isValid: false,
      error: `Search query must be less than ${MAX_SEARCH_QUERY_LENGTH} characters`,
    }
  }

  // Check for potentially malicious patterns
  const dangerousPatterns = [
    /<script[^>]*>[\s\S]*?<\/script>/gi, // Script tags
    /javascript:/gi, // JavaScript protocol
    /on\w+\s*=/gi, // Event handlers (onclick, onload, etc.)
    /<iframe[^>]*>/gi, // Iframe tags
    /<object[^>]*>/gi, // Object tags
    /<embed[^>]*>/gi, // Embed tags
  ]

  for (const pattern of dangerousPatterns) {
    if (pattern.test(query)) {
      return {
        isValid: false,
        error: 'Search query contains invalid characters or patterns',
      }
    }
  }

  return { isValid: true }
}

/**
 * Sanitizes text input by removing/escaping dangerous characters
 * 
 * @param input - The text to sanitize
 * @returns Sanitized text safe for display and API calls
 */
export function sanitizeTextInput(input: string): string {
  if (!input) return ''

  // Trim whitespace
  let sanitized = input.trim()

  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '')

  // Escape HTML special characters
  sanitized = sanitized
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')

  // Remove control characters except newlines and tabs
  sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '')

  return sanitized
}

// ============================================================================
// FILE UPLOAD VALIDATION
// ============================================================================

/**
 * Validates uploaded image file
 * 
 * @param file - The file to validate
 * @returns Validation result with error message if invalid
 */
export function validateImageFile(file: File): ValidationResult {
  // Check if file exists
  if (!file) {
    return {
      isValid: false,
      error: 'No file provided',
    }
  }

  // Check file size
  if (file.size === 0) {
    return {
      isValid: false,
      error: 'File is empty',
    }
  }

  if (file.size > MAX_FILE_SIZE) {
    return {
      isValid: false,
      error: `File size must be less than ${MAX_FILE_SIZE / (1024 * 1024)}MB`,
    }
  }

  // Check file type
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return {
      isValid: false,
      error: `Invalid file type. Allowed types: ${ALLOWED_IMAGE_TYPES.join(', ')}`,
    }
  }

  // Check file extension
  const fileName = file.name.toLowerCase()
  const hasValidExtension = ALLOWED_IMAGE_EXTENSIONS.some(ext => fileName.endsWith(ext))
  
  if (!hasValidExtension) {
    return {
      isValid: false,
      error: `Invalid file extension. Allowed extensions: ${ALLOWED_IMAGE_EXTENSIONS.join(', ')}`,
    }
  }

  // Check for path traversal attempts in filename
  if (file.name.includes('..') || file.name.includes('/') || file.name.includes('\\')) {
    return {
      isValid: false,
      error: 'Invalid file name',
    }
  }

  return { isValid: true }
}

/**
 * Sanitizes filename by removing dangerous characters
 * 
 * @param filename - The filename to sanitize
 * @returns Sanitized filename
 */
export function sanitizeFilename(filename: string): string {
  if (!filename) return 'image'

  // Remove path separators and parent directory references
  let sanitized = filename
    .replace(/\.\./g, '')
    .replace(/[\/\\]/g, '')

  // Remove special characters except dots, dashes, and underscores
  sanitized = sanitized.replace(/[^a-zA-Z0-9._-]/g, '_')

  // Limit length
  if (sanitized.length > 255) {
    const extension = sanitized.split('.').pop() || ''
    const nameWithoutExt = sanitized.substring(0, sanitized.lastIndexOf('.'))
    sanitized = nameWithoutExt.substring(0, 250 - extension.length) + '.' + extension
  }

  return sanitized
}

/**
 * Validates image content (basic check)
 * 
 * @param file - The image file to validate
 * @returns Promise with validation result
 */
export async function validateImageContent(file: File): Promise<ValidationResult> {
  return new Promise((resolve) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      const result = e.target?.result as string
      
      // Check if it's a valid data URL
      if (!result || !result.startsWith('data:image/')) {
        resolve({
          isValid: false,
          error: 'Invalid image format',
        })
        return
      }

      // Try to load as image to verify it's actually an image
      const img = new Image()
      img.onload = () => {
        // Check image dimensions (optional - can add min/max dimensions)
        if (img.width < 50 || img.height < 50) {
          resolve({
            isValid: false,
            error: 'Image dimensions too small (minimum 50x50px)',
          })
          return
        }

        if (img.width > 10000 || img.height > 10000) {
          resolve({
            isValid: false,
            error: 'Image dimensions too large (maximum 10000x10000px)',
          })
          return
        }

        resolve({ isValid: true })
      }
      
      img.onerror = () => {
        resolve({
          isValid: false,
          error: 'Failed to load image. File may be corrupted.',
        })
      }
      
      img.src = result
    }
    
    reader.onerror = () => {
      resolve({
        isValid: false,
        error: 'Failed to read file',
      })
    }
    
    reader.readAsDataURL(file)
  })
}

// ============================================================================
// RATE LIMITING
// ============================================================================

interface RateLimitConfig {
  maxRequests: number
  windowMs: number
}

class RateLimiter {
  private requests: number[] = []
  private config: RateLimitConfig

  constructor(config: RateLimitConfig) {
    this.config = config
  }

  /**
   * Checks if request is allowed under rate limit
   * 
   * @returns true if request is allowed, false if rate limited
   */
  checkLimit(): boolean {
    const now = Date.now()
    const windowStart = now - this.config.windowMs

    // Remove old requests outside the window
    this.requests = this.requests.filter(time => time > windowStart)

    // Check if under limit
    if (this.requests.length >= this.config.maxRequests) {
      return false
    }

    // Add current request
    this.requests.push(now)
    return true
  }

  /**
   * Gets time until next request is allowed (in ms)
   * 
   * @returns milliseconds until rate limit resets, or 0 if not rate limited
   */
  getTimeUntilReset(): number {
    if (this.requests.length < this.config.maxRequests) {
      return 0
    }

    const oldestRequest = this.requests[0]
    const resetTime = oldestRequest + this.config.windowMs
    return Math.max(0, resetTime - Date.now())
  }
}

// Export rate limiter instances for different operations
export const searchRateLimiter = new RateLimiter({
  maxRequests: 10, // 10 requests
  windowMs: 60000, // per minute
})

export const uploadRateLimiter = new RateLimiter({
  maxRequests: 5, // 5 uploads
  windowMs: 60000, // per minute
})
