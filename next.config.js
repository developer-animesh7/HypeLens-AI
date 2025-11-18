/** @type {import('next').NextConfig} */

/**
 * Validates required environment variables at build time
 * 
 * Ensures critical configuration is present before starting the application.
 * Throws descriptive errors with setup instructions if validation fails.
 */
function validateEnv() {
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  // Check required environment variable
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  
  if (!apiUrl) {
    console.error('\n❌ Environment Variable Error: NEXT_PUBLIC_API_URL is not defined\n');
    console.error('📝 To fix this issue:');
    console.error('   1. Copy .env.local.example to .env.local:');
    console.error('      cp .env.local.example .env.local\n');
    console.error('   2. Set NEXT_PUBLIC_API_URL in .env.local:');
    console.error('      NEXT_PUBLIC_API_URL=http://localhost:5000\n');
    console.error('   3. Ensure your FastAPI backend is running on port 5000\n');
    console.error('📖 See README.md for detailed setup instructions\n');
    
    throw new Error('Missing required environment variable: NEXT_PUBLIC_API_URL');
  }
  
  // Validate URL format
  try {
    const url = new URL(apiUrl);
    if (!url.protocol.startsWith('http')) {
      throw new Error('API URL must use HTTP or HTTPS protocol');
    }
    
    if (isDevelopment) {
      console.log(`✅ Environment validation passed`);
      console.log(`   API URL: ${apiUrl}`);
    }
  } catch (error) {
    console.error('\n❌ Environment Variable Error: Invalid NEXT_PUBLIC_API_URL format\n');
    console.error(`   Current value: ${apiUrl}\n`);
    console.error('📝 NEXT_PUBLIC_API_URL must be a valid URL:');
    console.error('   ✓ http://localhost:5000');
    console.error('   ✓ https://api.yourdomain.com');
    console.error('   ✗ localhost:5000 (missing protocol)');
    console.error('   ✗ /api (not a full URL)\n');
    
    throw new Error(`Invalid NEXT_PUBLIC_API_URL format: ${apiUrl}`);
  }
  
  // Check optional variables and log warnings
  const optionalVars = {
    NEXT_PUBLIC_APP_NAME: 'Application name (defaults to "HypeLens AI")',
    NEXT_PUBLIC_APP_VERSION: 'Application version (defaults to "1.0.0")',
    NEXT_PUBLIC_ENABLE_ANALYTICS: 'Analytics toggle (defaults to false)',
    NEXT_PUBLIC_MAX_IMAGE_SIZE: 'Max image size (defaults to 10MB)',
    NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT: 'Search results limit (defaults to 20)',
  };
  
  if (isDevelopment) {
    const missingOptional = Object.entries(optionalVars)
      .filter(([key]) => !process.env[key])
      .map(([key, desc]) => `   • ${key}: ${desc}`);
    
    if (missingOptional.length > 0) {
      console.log('\nℹ️  Optional environment variables not set (using defaults):');
      missingOptional.forEach(msg => console.log(msg));
      console.log('   See .env.local.example for configuration options\n');
    }
  }
}

// Validate environment variables before building
try {
  validateEnv();
} catch (error) {
  // Re-throw to stop the build process
  throw error;
}

/**
 * Security Headers Configuration
 * 
 * Configures comprehensive security headers to protect against common web vulnerabilities.
 * These headers are applied to all routes and provide defense-in-depth protection.
 * 
 * IMPORTANT: CORS (Cross-Origin Resource Sharing) is NOT configured here.
 * CORS is a backend security mechanism and is already properly handled by the
 * FastAPI backend in app.py (lines 154-160). Attempting to set CORS headers
 * in the frontend would be ineffective and architecturally incorrect.
 * 
 * Security Headers Applied:
 * - Content Security Policy (CSP): Prevents XSS attacks
 * - X-Frame-Options: Prevents clickjacking
 * - X-Content-Type-Options: Prevents MIME-sniffing
 * - Referrer-Policy: Controls referrer information
 * - Permissions-Policy: Restricts browser features
 * - HSTS: Forces HTTPS in production
 * 
 * Testing:
 * - Run: curl -I http://localhost:3000
 * - Check browser DevTools Console for CSP violations
 * - Verify HSTS only appears in production builds
 * - Ensure product images from external domains load correctly
 * - Confirm Next.js hot reload works in development
 * 
 * @returns Array of header configurations for all routes
 */
async function headers() {
  const isProduction = process.env.NODE_ENV === 'production';
  
  // Build Content Security Policy directives
  // Format: directive-name value1 value2; another-directive value;
  const cspDirectives = [
    // default-src: Fallback for all resource types not explicitly defined
    "default-src 'self'",
    
    // script-src: Control which scripts can execute
    // 'self': Allow scripts from same origin
    // 'unsafe-eval': Required for Next.js development mode and React features
    // 'unsafe-inline': Allow inline scripts (consider using nonces in production)
    "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
    
    // style-src: Control stylesheet sources
    // 'unsafe-inline': Required for Tailwind CSS and styled-components
    // https://fonts.googleapis.com: Google Fonts stylesheets
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    
    // font-src: Control font sources
    // https://fonts.gstatic.com: Google Fonts CDN
    // data:: Data URI fonts (base64 encoded)
    "font-src 'self' https://fonts.gstatic.com data:",
    
    // img-src: Control image sources
    // Allow all HTTPS/HTTP images for product images from various e-commerce platforms
    // (Amazon, Flipkart, Myntra, etc.)
    "img-src 'self' data: https: http:",
    
    // connect-src: Control fetch/XHR/WebSocket connections
    // Include both localhost variants for API calls to FastAPI backend
    "connect-src 'self' http://localhost:5000 http://127.0.0.1:5000",
    
    // frame-ancestors: Control where this page can be embedded
    // 'none': Prevent all iframe embedding (defense in depth with X-Frame-Options)
    "frame-ancestors 'none'",
    
    // base-uri: Restrict <base> tag URLs to prevent base tag injection attacks
    "base-uri 'self'",
    
    // form-action: Restrict form submission targets
    "form-action 'self'",
  ];
  
  // Add upgrade-insecure-requests only in production
  // Automatically upgrades HTTP requests to HTTPS
  if (isProduction) {
    cspDirectives.push('upgrade-insecure-requests');
  }
  
  // Join all CSP directives with semicolons
  const csp = cspDirectives.join('; ');
  
  // Build headers array
  const securityHeaders = [
    {
      // X-Frame-Options: Prevent clickjacking by blocking iframe embedding
      // DENY: Never allow this page to be embedded in an iframe
      key: 'X-Frame-Options',
      value: 'DENY',
    },
    {
      // X-Content-Type-Options: Prevent MIME-type sniffing
      // nosniff: Force browsers to respect declared Content-Type
      // Prevents browsers from interpreting files as different MIME types
      key: 'X-Content-Type-Options',
      value: 'nosniff',
    },
    {
      // Referrer-Policy: Control referrer information sent with requests
      // strict-origin-when-cross-origin: Send full URL for same-origin requests,
      // only origin for cross-origin HTTPS requests, nothing for HTTP downgrades
      key: 'Referrer-Policy',
      value: 'strict-origin-when-cross-origin',
    },
    {
      // Permissions-Policy: Restrict browser features (principle of least privilege)
      // Disable sensitive APIs that the app doesn't use to reduce attack surface
      key: 'Permissions-Policy',
      value: 'camera=(), microphone=(), geolocation=(), interest-cohort=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()',
    },
    {
      // X-DNS-Prefetch-Control: Allow DNS prefetching for performance
      // on: Allow browser to prefetch DNS for external domains
      // Improves loading speed for product images from e-commerce sites
      key: 'X-DNS-Prefetch-Control',
      value: 'on',
    },
    {
      // Content-Security-Policy: Comprehensive CSP to prevent XSS and injection attacks
      key: 'Content-Security-Policy',
      value: csp,
    },
  ];
  
  // Add HSTS only in production (localhost uses HTTP in development)
  if (isProduction) {
    securityHeaders.push({
      // Strict-Transport-Security (HSTS): Force HTTPS connections
      // max-age=31536000: Remember this policy for 1 year (in seconds)
      // includeSubDomains: Apply to all subdomains
      key: 'Strict-Transport-Security',
      value: 'max-age=31536000; includeSubDomains',
    });
  }
  
  return [
    {
      // Apply security headers to all routes
      source: '/:path*',
      headers: securityHeaders,
    },
  ];
}

const nextConfig = {
  /* config options here */
  eslint: {
    // Disable ESLint during builds (allows build to complete with warnings)
    ignoreDuringBuilds: true,
  },
  
  // Security headers for all routes
  headers,
  
  // Image optimization configuration
  images: {
    // Allow images from external e-commerce domains
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**', // Allow all HTTPS domains for product images from various e-commerce sites
      },
      {
        protocol: 'http',
        hostname: 'localhost', // Allow localhost for development
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1', // Allow 127.0.0.1 for development
      },
    ],
    // Image optimization formats
    formats: ['image/webp', 'image/avif'],
    // Device sizes for responsive images
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    // Image sizes for different breakpoints
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // Memory optimization for dev server
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Reduce memory usage in development
      config.watchOptions = {
        poll: 1000, // Check for changes every second
        aggregateTimeout: 300,
        ignored: ['**/node_modules/**', '**/.next/**', '**/venv/**', '**/__pycache__/**'],
      };
      
      // Enable filesystem caching with memory limits
      config.cache = {
        type: 'filesystem',
        maxMemoryGenerations: 1, // Only keep 1 generation in memory
        maxAge: 1000 * 60 * 60, // 1 hour cache
      };
      
      // Reduce chunk size to lower memory footprint
      config.optimization = {
        ...config.optimization,
        runtimeChunk: 'single',
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            commons: {
              name: 'commons',
              chunks: 'all',
              minChunks: 2,
            },
          },
        },
      };
    }
    
    return config;
  },
  
  // Experimental features for better performance
  experimental: {
    optimizePackageImports: ['framer-motion', 'react-icons'],
  },
};

module.exports = nextConfig;
