'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiSearch, FiCamera, FiUpload, FiX, FiTag } from 'react-icons/fi'
import { useDropzone } from 'react-dropzone'

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

export default function SearchSection() {
  const [searchMode, setSearchMode] = useState<'text' | 'image'>('text')
  const [searchQuery, setSearchQuery] = useState('')
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [categoryHint, setCategoryHint] = useState('')
  const [showCategoryHint, setShowCategoryHint] = useState(false)

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'] },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        const reader = new FileReader()
        reader.onload = () => {
          setUploadedImage(reader.result as string)
        }
        reader.readAsDataURL(file)
      }
    },
  })

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 search-section">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glass-card p-10 space-y-8"
        >
          {/* Mode Toggle */}
          <div className="flex justify-center">
            <div className="glass p-1.5 rounded-full inline-flex">
              <button
                onClick={() => setSearchMode('text')}
                className={`px-8 py-3.5 rounded-full font-medium transition-all ${
                  searchMode === 'text'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                }`}
              >
                <FiSearch className="inline-block mr-2" />
                Text Search
              </button>
              <button
                onClick={() => setSearchMode('image')}
                className={`px-8 py-3.5 rounded-full font-medium transition-all ${
                  searchMode === 'image'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                }`}
              >
                <FiCamera className="inline-block mr-2" />
                Visual Search
              </button>
            </div>
          </div>

          {/* Search Input */}
          <AnimatePresence mode="wait">
            {searchMode === 'text' ? (
              <motion.div
                key="text-search"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="relative"
              >
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search for products, brands, or categories..."
                  className="w-full px-6 py-5 pl-14 bg-slate-800/60 backdrop-blur-xl rounded-2xl text-lg text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all border border-slate-700/50 shadow-xl"
                />
                <FiSearch className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-blue-400" />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                  Search
                </motion.button>
              </motion.div>
            ) : (
              <motion.div
                key="image-search"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                {uploadedImage ? (
                  <div className="relative">
                    <img
                      src={uploadedImage}
                      alt="Uploaded"
                      className="w-full h-64 object-cover rounded-2xl"
                    />
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => {
                        setUploadedImage(null)
                        setCategoryHint('')
                        setShowCategoryHint(false)
                      }}
                      className="absolute top-4 right-4 p-2 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors"
                    >
                      <FiX className="w-5 h-5" />
                    </motion.button>
                    
                    {/* Category Hint Section */}
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-4 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <button
                          onClick={() => setShowCategoryHint(!showCategoryHint)}
                          className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <FiTag className="w-4 h-4" />
                          {showCategoryHint ? 'Hide category hint' : 'Image unclear? Add category hint (Optional)'}
                        </button>
                        {!showCategoryHint && (
                          <button
                            onClick={() => {
                              setShowCategoryHint(false)
                              setCategoryHint('')
                            }}
                            className="text-xs text-slate-400 hover:text-slate-300 transition-colors px-3 py-1 rounded-lg border border-slate-700 hover:border-slate-600"
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
                            className="space-y-3"
                          >
                            <select
                              value={categoryHint}
                              onChange={(e) => setCategoryHint(e.target.value)}
                              aria-label="Select product category"
                              className="w-full px-4 py-3 glass rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all bg-slate-800/50 border border-slate-700"
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
                                className="text-xs text-green-400 flex items-center gap-1"
                              >
                                ✓ Great! This will help our AI find better matches for your {categoryHint.toLowerCase()}
                              </motion.p>
                            )}
                            <div className="flex gap-2">
                              <button
                                onClick={() => {
                                  setShowCategoryHint(false)
                                  setCategoryHint('')
                                }}
                                className="flex-1 text-sm text-slate-400 hover:text-slate-300 transition-colors py-2 px-4 rounded-lg border border-slate-700 hover:border-slate-600"
                              >
                                Skip this step
                              </button>
                              {categoryHint && (
                                <button
                                  onClick={() => setShowCategoryHint(false)}
                                  className="flex-1 text-sm bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
                                >
                                  Continue →
                                </button>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>

                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all w-full mt-4"
                    >
                      Find Similar Products {categoryHint && `in ${categoryHint}`}
                    </motion.button>
                  </div>
                ) : (
                  <div
                    {...getRootProps()}
                    className={`relative border-2 border-dashed rounded-3xl p-16 text-center cursor-default transition-all overflow-hidden ${
                      isDragActive
                        ? 'border-blue-500 bg-blue-500/10 scale-105'
                        : 'border-slate-700 hover:border-blue-400 hover:bg-slate-800/30'
                    }`}
                  >
                    <input {...getInputProps()} />
                    
                    {/* Samsung Galaxy AI-inspired Background Animation */}
                    <div className="absolute inset-0 pointer-events-none overflow-hidden">
                      {/* Animated gradient orbs - optimized */}
                      <motion.div
                        className="absolute w-96 h-96 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-3xl"
                        animate={{
                          x: [-80, 80, -80],
                          y: [-40, 40, -40],
                          scale: [1, 1.1, 1],
                        }}
                        transition={{
                          duration: 20,
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                        style={{ top: '20%', left: '10%' }}
                      />
                      <motion.div
                        className="absolute w-80 h-80 rounded-full bg-gradient-to-r from-pink-500/20 to-purple-500/20 blur-3xl"
                        animate={{
                          x: [80, -80, 80],
                          y: [40, -40, 40],
                          scale: [1.1, 1, 1.1],
                        }}
                        transition={{
                          duration: 25,
                          repeat: Infinity,
                          ease: "easeInOut",
                          delay: 1
                        }}
                        style={{ bottom: '20%', right: '10%' }}
                      />
                      
                      {/* Floating particles - optimized (6 instead of 12) */}
                      {[...Array(6)].map((_, i) => (
                        <motion.div
                          key={i}
                          className="absolute w-2 h-2 rounded-full"
                          style={{
                            background: `linear-gradient(135deg, ${
                              i % 2 === 0 ? '#3b82f6' : '#8b5cf6'
                            }, transparent)`,
                            left: `${15 + i * 15}%`,
                            top: `${20 + i * 12}%`,
                          }}
                          animate={{
                            y: [-15, 15, -15],
                            opacity: [0.3, 0.7, 0.3],
                            scale: [1, 1.3, 1],
                          }}
                          transition={{
                            duration: 4,
                            repeat: Infinity,
                            delay: i * 0.3,
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
                      
                      {/* AI Sparkles - optimized (3 instead of 4) */}
                      {[...Array(3)].map((_, i) => (
                        <motion.div
                          key={i}
                          className="absolute w-1 h-1 bg-blue-400 rounded-full"
                          style={{
                            top: `${50 + Math.cos((i * Math.PI * 2) / 3) * 50}%`,
                            left: `${50 + Math.sin((i * Math.PI * 2) / 3) * 50}%`,
                          }}
                          animate={{
                            scale: [0, 1.3, 0],
                            opacity: [0, 0.9, 0],
                          }}
                          transition={{
                            duration: 2.5,
                            repeat: Infinity,
                            delay: i * 0.6,
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
            )}
          </AnimatePresence>

          {/* Quick Suggestions */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-dark-500 dark:text-dark-400">Popular:</span>
            {['Smartphones', 'Laptops', 'Headphones', 'Watches', 'Cameras'].map((tag) => (
              <motion.button
                key={tag}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSearchQuery(tag)}
                className="px-4 py-1 glass rounded-full text-sm hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
              >
                {tag}
              </motion.button>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
