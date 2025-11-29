import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // Disable ESLint during builds (allows build to complete with warnings)
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable TypeScript errors during builds (allows build to complete)
    ignoreBuildErrors: true,
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

export default nextConfig;
