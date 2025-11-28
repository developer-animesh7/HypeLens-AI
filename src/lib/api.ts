import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

/**
 * Centralized Axios Instance for API Communication
 * 
 * This module provides a configured axios instance with:
 * - Base URL configuration from environment variables (.env.local)
 * - Automatic validation of API URL format at module load
 * - Request/response interceptors for error handling
 * - CSRF token support (prepared for future backend implementation)
 * - Comprehensive error handling with user-friendly messages
 * - Development mode logging for debugging
 * 
 * Environment Variables:
 * - NEXT_PUBLIC_API_URL: Backend API base URL (required)
 *   See .env.local.example for configuration template
 *   Validated at build time by next.config.ts
 * 
 * Usage:
 * ```typescript
 * import api from '@/lib/api';
 * const response = await api.post('/api/semantic-search', { query: 'laptop' });
 * ```
 * 
 * Troubleshooting:
 * - If you see connection errors, verify backend is running: curl http://localhost:5000/health
 * - Check NEXT_PUBLIC_API_URL in .env.local matches backend server address
 * - Ensure backend CORS allows requests from http://localhost:3000
 * 
 * @see .env.local.example - Environment variable template
 * @see next.config.ts - Build-time environment validation
 * @see README.md - Detailed setup instructions
 */

// ============================================================================
// CONFIGURATION VALIDATION
// ============================================================================

/**
 * Validates and normalizes the API URL configuration
 * Runs at module load to catch configuration errors early
 */
function validateApiConfig(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  // Validate URL format
  try {
    const url = new URL(apiUrl);
    if (!url.protocol.startsWith('http')) {
      throw new Error('API URL must use HTTP or HTTPS protocol');
    }
    
    // Log configuration in development mode
    if (isDevelopment) {
      if (!process.env.NEXT_PUBLIC_API_URL) {
        console.warn('[API Client] ⚠️  NEXT_PUBLIC_API_URL not set, using fallback: http://localhost:5000');
        console.warn('[API Client] 💡 Create .env.local from .env.local.example to configure');
      } else {
        console.log(`[API Client] ✅ Using API URL: ${apiUrl}`);
      }
    }
    
    return apiUrl;
  } catch (error) {
    console.error('[API Client] ❌ Invalid NEXT_PUBLIC_API_URL format:', apiUrl);
    console.error('[API Client] 📝 URL must include protocol (http:// or https://)');
    console.error('[API Client] 💡 See .env.local.example for valid examples');
    
    // In development, use fallback; in production, throw error
    if (isDevelopment) {
      console.warn('[API Client] ⚠️  Using fallback: http://localhost:5000');
      return 'http://localhost:5000';
    } else {
      throw new Error(`Invalid API URL configuration: ${apiUrl}`);
    }
  }
}

// Validate configuration at module load
const BASE_URL = validateApiConfig();

// ============================================================================
// BASE CONFIGURATION
// ============================================================================

const api: AxiosInstance = axios.create({
  // Use validated API URL
  baseURL: BASE_URL,
  
  // 15 second timeout to handle slower semantic search operations
  timeout: 15000,
  
  // Default headers for JSON communication
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Enable credentials for future cookie-based authentication
  withCredentials: true,
});

// ============================================================================
// CSRF TOKEN HELPERS (Prepared for Future Backend Implementation)
// ============================================================================

/**
 * Retrieves CSRF token from multiple possible sources
 * Currently prepared for future backend CSRF implementation
 * 
 * Checks in order:
 * 1. Cookie (csrftoken or XSRF-TOKEN)
 * 2. Meta tag in HTML head
 * 3. localStorage
 * 
 * @returns CSRF token string or null if not found
 */
export const getCsrfToken = (): string | null => {
  // Check cookies
  if (typeof document !== 'undefined') {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken' || name === 'XSRF-TOKEN') {
        return decodeURIComponent(value);
      }
    }
    
    // Check meta tag
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
      return metaTag.getAttribute('content');
    }
  }
  
  // Check localStorage (SSR-safe check)
  if (typeof window !== 'undefined' && window.localStorage) {
    return localStorage.getItem('csrfToken');
  }
  
  return null;
};

/**
 * Stores CSRF token in localStorage for future requests
 * 
 * @param token - CSRF token to store
 */
export const setCsrfToken = (token: string): void => {
  if (typeof window !== 'undefined' && window.localStorage) {
    localStorage.setItem('csrfToken', token);
  }
};

// ============================================================================
// REQUEST INTERCEPTOR
// ============================================================================

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add timestamp for debugging purposes
    const timestamp = new Date().toISOString();
    config.headers.set('X-Request-Timestamp', timestamp);
    
    // Add CSRF token if available (prepared for future backend implementation)
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers.set('X-CSRF-Token', csrfToken);
    }
    
    // Log request in development mode
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        timestamp,
        data: config.data,
        params: config.params,
      });
    }
    
    return config;
  },
  (error: AxiosError) => {
    // Handle request setup errors
    if (process.env.NODE_ENV === 'development') {
      console.error('[API Request Error]', error);
    }
    
    return Promise.reject({
      message: 'Failed to setup request. Please try again.',
      status: null,
      originalError: error,
    });
  }
);

// ============================================================================
// RESPONSE INTERCEPTORS
// ============================================================================

/**
 * Success Response Interceptor (2xx status codes)
 */
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development mode
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }
    
    // Return response.data directly for cleaner API usage
    return response;
  },
  
  /**
   * Error Response Interceptor (4xx/5xx status codes and network errors)
   */
  (error: AxiosError) => {
    // Structure for error object
    interface ApiError {
      message: string;
      status: number | null;
      originalError: AxiosError;
    }
    
    let apiError: ApiError = {
      message: 'An unexpected error occurred. Please try again.',
      status: null,
      originalError: error,
    };
    
    if (error.response) {
      // Server responded with error status code
      const status = error.response.status;
      const data = error.response.data as any;
      
      // Extract error message from response
      const serverMessage = data?.detail || data?.message || data?.error;
      
      switch (status) {
        case 400:
          // Bad Request - validation errors
          apiError = {
            message: serverMessage || 'Invalid request. Please check your input and try again.',
            status,
            originalError: error,
          };
          break;
          
        case 401:
          // Unauthorized - authentication required
          apiError = {
            message: 'Authentication required. Please log in to continue.',
            status,
            originalError: error,
          };
          // TODO: Redirect to login page when authentication is implemented
          // if (typeof window !== 'undefined') {
          //   window.location.href = '/login';
          // }
          break;
          
        case 403:
          // Forbidden - access denied
          apiError = {
            message: 'Access denied. You do not have permission to perform this action.',
            status,
            originalError: error,
          };
          break;
          
        case 404:
          // Not Found
          apiError = {
            message: serverMessage || 'The requested resource was not found.',
            status,
            originalError: error,
          };
          break;
          
        case 429:
          // Too Many Requests - rate limiting
          apiError = {
            message: 'Too many requests. Please wait a moment and try again.',
            status,
            originalError: error,
          };
          break;
          
        case 500:
          // Internal Server Error
          apiError = {
            message: 'Server error occurred. Please try again later.',
            status,
            originalError: error,
          };
          break;
          
        case 503:
          // Service Unavailable - relevant for ML model loading
          apiError = {
            message: 'Service is currently initializing. Please try again in a moment.',
            status,
            originalError: error,
          };
          break;
          
        default:
          // Other error status codes
          apiError = {
            message: serverMessage || `Request failed with status ${status}. Please try again.`,
            status,
            originalError: error,
          };
      }
      
      // Log error in development mode
      if (process.env.NODE_ENV === 'development') {
        console.error(`[API Error] ${status} ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
          message: apiError.message,
          response: error.response.data,
        });
      }
      
    } else if (error.request) {
      // Request was made but no response received (network error)
      apiError = {
        message: 'Network error. Please check your internet connection and try again.',
        status: null,
        originalError: error,
      };
      
      if (process.env.NODE_ENV === 'development') {
        console.error('[API Network Error]', {
          message: apiError.message,
          request: error.request,
        });
      }
      
    } else {
      // Error in request setup
      apiError = {
        message: 'Failed to send request. Please try again.',
        status: null,
        originalError: error,
      };
      
      if (process.env.NODE_ENV === 'development') {
        console.error('[API Setup Error]', error.message);
      }
    }
    
    return Promise.reject(apiError);
  }
);

// ============================================================================
// EXPORTS
// ============================================================================

export default api;
