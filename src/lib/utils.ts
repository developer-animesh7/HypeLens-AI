import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility Functions for the AI Shopping Helper Application
 * 
 * This module provides commonly used utility functions for:
 * - ClassName merging with Tailwind CSS conflict resolution
 * - Currency formatting with locale support
 * - Text manipulation and formatting
 * - Number formatting
 * - Debouncing
 * - Image placeholder generation
 */

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

/**
 * Supported currency codes for formatting
 */
export type Currency = 'INR' | 'USD' | 'EUR' | 'GBP' | 'JPY' | 'AUD' | 'CAD';

// ============================================================================
// CLASSNAME UTILITIES
// ============================================================================

/**
 * Merges multiple className values and resolves Tailwind CSS conflicts
 * 
 * Uses clsx for conditional class handling and tailwind-merge for intelligent
 * merging of Tailwind classes. When conflicting utilities are provided
 * (e.g., px-4 and px-6), only the last one is kept.
 * 
 * @param inputs - Multiple className values (strings, objects, arrays)
 * @returns Merged className string with conflicts resolved
 * 
 * @example
 * cn('px-4 py-2', isActive && 'bg-blue-500', className)
 * // Returns: "px-4 py-2 bg-blue-500 custom-class"
 * 
 * @example
 * cn('px-4', 'px-6') // Only 'px-6' is kept
 * cn('text-sm', condition && 'text-lg') // Conditional classes
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

// ============================================================================
// CURRENCY FORMATTING
// ============================================================================

/**
 * Currency symbol mapping for common currencies
 */
const CURRENCY_SYMBOLS: Record<Currency, string> = {
  INR: '₹',
  USD: '$',
  EUR: '€',
  GBP: '£',
  JPY: '¥',
  AUD: 'A$',
  CAD: 'C$',
};

/**
 * Locale mapping for currency formatting
 */
const CURRENCY_LOCALES: Record<Currency, string> = {
  INR: 'en-IN',
  USD: 'en-US',
  EUR: 'en-US',
  GBP: 'en-GB',
  JPY: 'ja-JP',
  AUD: 'en-AU',
  CAD: 'en-CA',
};

/**
 * Formats a number as currency with proper symbol and locale formatting
 * 
 * Uses Intl.NumberFormat for proper number formatting with locale support.
 * Handles Indian numbering system (lakhs/crores) for INR and standard
 * international formatting for other currencies.
 * 
 * @param amount - The numeric amount to format
 * @param currencyCode - The currency code (default: 'INR')
 * @returns Formatted currency string with symbol
 * 
 * @example
 * formatCurrency(150000, 'INR')
 * // Returns: "₹1,50,000"
 * 
 * @example
 * formatCurrency(1234.56, 'USD')
 * // Returns: "$1,234.56"
 * 
 * @example
 * formatCurrency(0, 'EUR')
 * // Returns: "€0"
 * 
 * @example
 * formatCurrency(-500, 'GBP')
 * // Returns: "-£500"
 */
export function formatCurrency(amount: number, currencyCode: Currency = 'INR'): string {
  // Handle edge cases
  if (!isFinite(amount)) {
    return `${CURRENCY_SYMBOLS[currencyCode]}0`;
  }

  // Get locale for the currency
  const locale = CURRENCY_LOCALES[currencyCode];
  
  // Format the number based on locale
  const formatter = new Intl.NumberFormat(locale, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
  
  const formattedAmount = formatter.format(Math.abs(amount));
  const symbol = CURRENCY_SYMBOLS[currencyCode];
  
  // Handle negative amounts
  if (amount < 0) {
    return `-${symbol}${formattedAmount}`;
  }
  
  return `${symbol}${formattedAmount}`;
}

// ============================================================================
// TEXT UTILITIES
// ============================================================================

/**
 * Truncates text to specified length, preferring word boundaries
 * 
 * Intelligently truncates text without cutting words in half when possible.
 * If the text is shorter than maxLength, returns it unchanged.
 * 
 * @param text - The text to truncate
 * @param maxLength - Maximum length before truncation (default: 100)
 * @param suffix - String to append when truncated (default: '...')
 * @returns Truncated text with suffix if needed
 * 
 * @example
 * truncateText('This is a very long product description', 20)
 * // Returns: "This is a very long..."
 * 
 * @example
 * truncateText('Short text', 50)
 * // Returns: "Short text"
 * 
 * @example
 * truncateText('Product name', 10, '…')
 * // Returns: "Product…"
 */
export function truncateText(text: string, maxLength: number = 100, suffix: string = '...'): string {
  if (!text || text.length <= maxLength) {
    return text;
  }
  
  // Find the last space before maxLength to avoid cutting words
  const truncateAt = text.lastIndexOf(' ', maxLength);
  
  // If no space found or it's too early in the string, just cut at maxLength
  if (truncateAt === -1 || truncateAt < maxLength * 0.8) {
    return text.substring(0, maxLength).trim() + suffix;
  }
  
  return text.substring(0, truncateAt).trim() + suffix;
}

/**
 * Legacy truncate function for backward compatibility
 * @deprecated Use truncateText instead
 */
export function truncate(str: string, length: number = 100): string {
  return truncateText(str, length);
}

// ============================================================================
// NUMBER FORMATTING
// ============================================================================

/**
 * Formats numbers with thousand separators using Indian numbering system
 * 
 * Uses the Indian numbering system where separators are placed at thousands,
 * lakhs (hundred thousands), and crores (ten millions).
 * 
 * @param num - The number to format
 * @returns Formatted number string with separators
 * 
 * @example
 * formatNumber(1000)
 * // Returns: "1,000"
 * 
 * @example
 * formatNumber(100000)
 * // Returns: "1,00,000" (1 lakh)
 * 
 * @example
 * formatNumber(10000000)
 * // Returns: "1,00,00,000" (1 crore)
 */
export function formatNumber(num: number): string {
  if (!isFinite(num)) {
    return '0';
  }
  
  const formatter = new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 2,
  });
  
  return formatter.format(num);
}

// ============================================================================
// FUNCTION UTILITIES
// ============================================================================

/**
 * Creates a debounced function that delays execution until after delay milliseconds
 * 
 * Useful for rate-limiting expensive operations like API calls or search queries.
 * The function will only execute after the specified delay has passed since
 * the last call.
 * 
 * @param func - The function to debounce
 * @param delay - Delay in milliseconds (default: 300)
 * @returns Debounced version of the function
 * 
 * @example
 * const debouncedSearch = debounce((query: string) => {
 *   // API call
 *   searchProducts(query);
 * }, 500);
 * 
 * // User types rapidly
 * debouncedSearch('laptop'); // Won't execute
 * debouncedSearch('laptop '); // Won't execute
 * debouncedSearch('laptop pro'); // Executes after 500ms
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null;
  
  return function debounced(...args: Parameters<T>): void {
    // Clear existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    // Set new timeout
    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
}

// ============================================================================
// IMAGE UTILITIES
// ============================================================================

/**
 * Generates a placeholder image URL for missing product images
 * 
 * Creates a placeholder using an online service that generates simple
 * text-based placeholder images. Useful for displaying when product
 * images fail to load or are unavailable.
 * 
 * @param text - Text to display in placeholder (default: 'No Image')
 * @returns Placeholder image URL
 * 
 * @example
 * getImagePlaceholder()
 * // Returns: "https://via.placeholder.com/400x400?text=No+Image"
 * 
 * @example
 * getImagePlaceholder('Product')
 * // Returns: "https://via.placeholder.com/400x400?text=Product"
 */
export function getImagePlaceholder(text: string = 'No Image'): string {
  const encodedText = encodeURIComponent(text);
  return `https://via.placeholder.com/400x400?text=${encodedText}`;
}

// ============================================================================
// ADDITIONAL UTILITY FUNCTIONS
// ============================================================================

/**
 * Safely parses a JSON string with fallback value
 * 
 * @param jsonString - JSON string to parse
 * @param fallback - Fallback value if parsing fails
 * @returns Parsed object or fallback value
 */
export function safeJsonParse<T>(jsonString: string, fallback: T): T {
  try {
    return JSON.parse(jsonString) as T;
  } catch {
    return fallback;
  }
}

/**
 * Generates a random ID string
 * 
 * @param prefix - Optional prefix for the ID
 * @returns Random ID string
 */
export function generateId(prefix: string = 'id'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Checks if a value is empty (null, undefined, empty string, empty array, empty object)
 * 
 * @param value - Value to check
 * @returns True if value is empty
 */
export function isEmpty(value: any): boolean {
  if (value == null) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}

/**
 * Capitalizes the first letter of a string
 * 
 * @param str - String to capitalize
 * @returns Capitalized string
 */
export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Formats a date relative to now (e.g., "2 hours ago", "yesterday")
 * 
 * @param date - Date to format
 * @returns Relative time string
 */
export function formatRelativeTime(date: Date | string | number): string {
  const now = new Date();
  const then = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000);
  
  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
  
  return then.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
}
