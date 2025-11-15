'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiCamera, FiUpload, FiX, FiTag, FiArrowRight, FiZap } from 'react-icons/fi'
import { useDropzone } from 'react-dropzone'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import CursorFollower from '@/components/layout/CursorFollower'
import VisualSearchResults from '@/components/search/VisualSearchResults'
import { visualSearch, Product } from '@/services/productService'

const categoryHints = [
  'Smartphone',
  'Laptop',
  'Headphones',
  'Watch',
  'Camera',
  'Tablet',
  'Speaker',
  'TV',
  'Gaming Console',
  'Accessories'
]

export default function VisualSearchPage() {
  const [uploadedImage, setUploadedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [categoryHint, setCategoryHint] = useState('')
  const [showCategoryHint, setShowCategoryHint] = useState(false)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<Product[]>([])
  const [searchTime, setSearchTime] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        setUploadedImage(file)
        
        // Create preview
        const reader = new FileReader()
        reader.onload = () => {
          setImagePreview(reader.result as string)
        }
        reader.readAsDataURL(file)
        
        // Reset previous results
        setResults([])
        setError(null)
        setHasSearched(false)
      }
    },
  })

  const handleSearch = async () => {
    if (!uploadedImage) {
      setError('Please upload an image first')
      return
    }

    setLoading(true)
    setError(null)
    const startTime = performance.now()

    try {
      const response = await visualSearch(
        uploadedImage,
        categoryHint || undefined,
        20
      )
      
      const endTime = performance.now()
      setSearchTime((endTime - startTime) / 1000)
      
      setResults(response.results)
      setHasSearched(true)
      
      if (response.results.length === 0) {
        setError('No similar products found. Try a different image or category.')
      }
    } catch (err: any) {
      console.error('Visual search error:', err)
      setError(err.response?.data?.detail || 'Failed to search. Please make sure the backend server is running on port 5000.')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setUploadedImage(null)
    setImagePreview(null)
    setCategoryHint('')
    setShowCategoryHint(false)
    setResults([])
    setError(null)
    setHasSearched(false)
    setSearchTime(0)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <CursorFollower />
      <Header />
      
      <main className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <motion.div
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-block mb-4"
            >
              <div className="glass px-6 py-3 rounded-full text-sm font-semibold text-blue-400 inline-flex items-center gap-2">
                <FiCamera className="w-4 h-4" />
                AI-Powered Visual Search
              </div>
            </motion.div>
            
            <h1 className="text-5xl md:text-6xl font-bold mb-4 font-outfit">
              Find Products by{' '}
              <span className="gradient-text">Image</span>
            </h1>
            
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Upload any product image and let our CLIP-powered AI find similar items from thousands of products
            </p>
          </motion.div>

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-8 md:p-12 mb-12"
          >
            {imagePreview ? (
              <div className="space-y-6">
                {/* Image Preview */}
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Uploaded"
                    className="w-full max-h-96 object-contain rounded-2xl bg-slate-800/50"
                  />
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={handleReset}
                    className="absolute top-4 right-4 p-3 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors"
                  >
                    <FiX className="w-5 h-5" />
                  </motion.button>
                </div>

                {/* Category Hint Section */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => setShowCategoryHint(!showCategoryHint)}
                      className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      <FiTag className="w-4 h-4" />
                      {showCategoryHint ? 'Hide category hint' : 'Add category hint for better results (Optional)'}
                    </button>
                    {!showCategoryHint && (
                      <button
                        onClick={() => {
                          setShowCategoryHint(false)
                          setCategoryHint('')
                        }}
                        className="text-xs text-slate-400 hover:text-slate-300 transition-colors px-4 py-2 rounded-lg border border-slate-700 hover:border-slate-600"
                      >
                        Skip →
                      </button>
                    )}
                  </div>

                  <AnimatePresence>
                    {showCategoryHint && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="space-y-4"
                      >
                        <select
                          value={categoryHint}
                          onChange={(e) => setCategoryHint(e.target.value)}
                          className="w-full px-4 py-3 glass rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-800/50 border border-slate-700 text-white"
                        >
                          <option value="">Select product category...</option>
                          {categoryHints.map((hint) => (
                            <option key={hint} value={hint}>
                              {hint}
                            </option>
                          ))}
                        </select>
                        {categoryHint && (
                          <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-sm text-green-400 flex items-center gap-2"
                          >
                            <FiZap className="w-4 h-4" />
                            Great! Searching for {categoryHint} specifically will improve accuracy
                          </motion.p>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>

                {/* Search Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSearch}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                      />
                      Searching with AI...
                    </>
                  ) : (
                    <>
                      <FiCamera className="w-5 h-5" />
                      Find Similar Products {categoryHint && `in ${categoryHint}`}
                      <FiArrowRight className="w-5 h-5" />
                    </>
                  )}
                </motion.button>
              </div>
            ) : (
              <div
                {...getRootProps()}
                className={`relative border-2 border-dashed rounded-3xl p-16 text-center cursor-pointer transition-all overflow-hidden ${
                  isDragActive
                    ? 'border-blue-500 bg-blue-500/10 scale-105'
                    : 'border-slate-700 hover:border-blue-400 hover:bg-slate-800/30'
                }`}
              >
                <input {...getInputProps()} />
                
                {/* Samsung Galaxy AI-inspired Background Animation */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                  {/* Animated gradient orbs */}
                  <motion.div
                    className="absolute w-96 h-96 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-3xl"
                    animate={{
                      x: [-100, 100, -100],
                      y: [-50, 50, -50],
                      scale: [1, 1.2, 1],
                    }}
                    transition={{
                      duration: 15,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                    style={{ top: '20%', left: '10%' }}
                  />
                  <motion.div
                    className="absolute w-80 h-80 rounded-full bg-gradient-to-r from-pink-500/20 to-purple-500/20 blur-3xl"
                    animate={{
                      x: [100, -100, 100],
                      y: [50, -50, 50],
                      scale: [1.2, 1, 1.2],
                    }}
                    transition={{
                      duration: 18,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: 1
                    }}
                    style={{ bottom: '20%', right: '10%' }}
                  />
                  
                  {/* Floating particles - Galaxy AI style */}
                  {[...Array(12)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-2 h-2 rounded-full"
                      style={{
                        background: `linear-gradient(135deg, ${
                          i % 3 === 0 ? '#3b82f6' : i % 3 === 1 ? '#8b5cf6' : '#ec4899'
                        }, transparent)`,
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                      }}
                      animate={{
                        y: [-20, 20, -20],
                        x: [-10, 10, -10],
                        opacity: [0.2, 0.8, 0.2],
                        scale: [1, 1.5, 1],
                      }}
                      transition={{
                        duration: 3 + Math.random() * 2,
                        repeat: Infinity,
                        delay: i * 0.2,
                        ease: "easeInOut"
                      }}
                    />
                  ))}
                  
                  {/* Scanning lines - AI effect */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-500/10 to-transparent"
                    animate={{
                      y: ['-100%', '200%'],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: "linear"
                    }}
                  />
                </div>

                {/* Upload Icon with AI Animation */}
                <motion.div
                  animate={{
                    y: isDragActive ? -10 : 0,
                    scale: isDragActive ? 1.1 : 1,
                  }}
                  className="relative inline-block mb-6"
                >
                  {/* Glowing ring */}
                  <motion.div
                    className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 opacity-20 blur-xl"
                    animate={{
                      scale: [1, 1.3, 1],
                      opacity: [0.2, 0.4, 0.2],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  />
                  
                  {/* Icon container */}
                  <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-blue-600/20 to-purple-600/20 backdrop-blur-sm border-2 border-blue-500/30 flex items-center justify-center">
                    <FiUpload className="w-12 h-12 text-blue-400" />
                    
                    {/* Rotating ring */}
                    <motion.div
                      className="absolute inset-0 rounded-full border-2 border-transparent"
                      style={{
                        borderTopColor: '#3b82f6',
                        borderRightColor: '#8b5cf6',
                      }}
                      animate={{ rotate: 360 }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "linear"
                      }}
                    />
                  </div>
                  
                  {/* AI Sparkles */}
                  {[...Array(4)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-1 h-1 bg-blue-400 rounded-full"
                      style={{
                        top: `${50 + Math.cos((i * Math.PI) / 2) * 50}%`,
                        left: `${50 + Math.sin((i * Math.PI) / 2) * 50}%`,
                      }}
                      animate={{
                        scale: [0, 1.5, 0],
                        opacity: [0, 1, 0],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        delay: i * 0.5,
                      }}
                    />
                  ))}
                </motion.div>

                {/* Text with gradient */}
                <motion.p
                  className="text-3xl font-bold mb-3 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent font-outfit"
                  animate={{
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                  }}
                  transition={{
                    duration: 5,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                  style={{
                    backgroundSize: '200% 200%',
                  }}
                >
                  {isDragActive ? 'Drop your image here' : 'Upload Product Image'}
                </motion.p>
                
                <p className="text-slate-300 mb-4 text-lg">
                  Drag & drop or click to browse
                </p>
                
                <div className="inline-flex items-center gap-2 text-sm text-slate-500 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700/50">
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                  AI-Powered • PNG, JPG, JPEG, GIF or WEBP (Max 10MB)
                </div>
              </div>
            )}
          </motion.div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-6 mb-8 border-2 border-red-500/50 bg-red-500/10"
            >
              <p className="text-red-400 text-center font-medium">⚠️ {error}</p>
            </motion.div>
          )}

          {/* Results Section */}
          {hasSearched && (
            <VisualSearchResults 
              results={results}
              loading={loading}
              searchTime={searchTime}
            />
          )}

          {/* Instructions */}
          {!hasSearched && !imagePreview && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid md:grid-cols-3 gap-6 mt-12"
            >
              {[
                {
                  icon: '📸',
                  title: 'Upload Image',
                  description: 'Take a photo or upload an existing product image'
                },
                {
                  icon: '🤖',
                  title: 'AI Analysis',
                  description: 'Our CLIP model analyzes the image with 768-dim embeddings'
                },
                {
                  icon: '🎯',
                  title: 'Get Results',
                  description: 'Find similar products from 1M+ items in milliseconds'
                }
              ].map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="glass-card p-6 text-center"
                >
                  <div className="text-4xl mb-3">{step.icon}</div>
                  <h3 className="text-xl font-semibold text-white mb-2 font-outfit">
                    {step.title}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    {step.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}
