/**
 * TypeScript Type Definitions for Environment Variables
 * 
 * This file provides type safety and IntelliSense support for environment
 * variables used throughout the HypeLens AI application.
 * 
 * This file is automatically included by TypeScript via tsconfig.json
 * configuration and does not need to be explicitly imported.
 * 
 * Usage:
 *   const apiUrl = process.env.NEXT_PUBLIC_API_URL; // TypeScript knows this is a string
 *   const analytics = process.env.NEXT_PUBLIC_ENABLE_ANALYTICS; // TypeScript knows this is string | undefined
 * 
 * @see .env.local.example for documentation on each environment variable
 */

declare namespace NodeJS {
  interface ProcessEnv {
    /**
     * Backend API Base URL
     * 
     * Points to the FastAPI backend server. Required for all API communication.
     * 
     * @example "http://localhost:5000" // Development
     * @example "https://api.yourdomain.com" // Production
     */
    NEXT_PUBLIC_API_URL: string;

    /**
     * Application Name for Branding
     * 
     * Used in page titles, headers, and other UI elements.
     * 
     * @default "HypeLens AI"
     * @example "HypeLens AI"
     */
    NEXT_PUBLIC_APP_NAME?: string;

    /**
     * Application Version
     * 
     * Displayed in the footer and about section.
     * 
     * @default "1.0.0"
     * @example "1.0.0"
     * @example "2.1.3"
     */
    NEXT_PUBLIC_APP_VERSION?: string;

    /**
     * Enable Analytics Tracking
     * 
     * Toggle for analytics services (Google Analytics, etc.).
     * Note: Environment variables are always strings, so "true" and "false" are strings.
     * 
     * @default "false"
     * @example "true"
     * @example "false"
     */
    NEXT_PUBLIC_ENABLE_ANALYTICS?: string;

    /**
     * Maximum Image Upload Size (bytes)
     * 
     * Limits the size of images that can be uploaded for visual search.
     * Note: Environment variables are always strings, parse to number when using.
     * 
     * @default "10485760" // 10 MB
     * @example "5242880" // 5 MB
     * @example "20971520" // 20 MB
     */
    NEXT_PUBLIC_MAX_IMAGE_SIZE?: string;

    /**
     * Default Search Results Limit
     * 
     * Number of search results to display per page.
     * Note: Environment variables are always strings, parse to number when using.
     * 
     * @default "20"
     * @example "10"
     * @example "50"
     */
    NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT?: string;

    /**
     * Node Environment
     * 
     * Automatically set by Next.js. Determines the runtime environment.
     * 
     * @readonly
     */
    NODE_ENV: 'development' | 'production' | 'test';
  }
}

// Export empty object to make this a module
export {};
