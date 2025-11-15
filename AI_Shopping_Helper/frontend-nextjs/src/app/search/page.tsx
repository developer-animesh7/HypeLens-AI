'use client'

import { useState, useEffect } from 'react'
import { FiSearch, FiCamera, FiUpload, FiX, FiTag, FiArrowLeft } from 'react-icons/fi'
import { useDropzone } from 'react-dropzone'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import CursorFollower from '@/components/layout/CursorFollower'
import Link from 'next/link'

const categoryHints = [
  'Smartphone', 'Laptop', 'Headphones', 'Watch', 'Camera',
  'Tablet', 'Speaker', 'TV', 'Gaming Console', 'Accessories'
]

export default function SearchPage() {
  const [searchMode, setSearchMode] = useState<'text' | 'image'>('text')
  const [searchQuery, setSearchQuery] = useState('')
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [categoryHint, setCategoryHint] = useState('')
  const [showCategoryHint, setShowCategoryHint] = useState(false)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'] },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        const reader = new FileReader()
        reader.onload = () => setUploadedImage(reader.result as string)
        reader.readAsDataURL(file)
      }
    },
  })

  return (
    <div className="min-h-screen bg-slate-950">
      <CursorFollower />
      <Header />
      
      <main className={`pt-24 pb-20 px-4 sm:px-6 lg:px-8 transition-all duration-500 ease-out ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      }`}>
        <div className="max-w-5xl mx-auto">
          {/* Back Button */}
          <Link href="/" className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition-colors mb-8">
            <FiArrowLeft className="w-5 h-5" />
            Back to Home
          </Link>

          {/* Title */}
          <div className={`text-center mb-12 transition-all duration-700 delay-100 ease-out ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 font-outfit">
              Search Your Perfect Product
            </h1>
            <p className="text-xl text-slate-300">
              Use text or image to find exactly what you're looking for
            </p>
          </div>

          {/* Search Card */}
          <div className={`glass-card p-8 md:p-12 space-y-8 transition-all duration-700 delay-200 ease-out ${
            isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
          }`}>
            {/* Mode Toggle Buttons */}
            <div className="flex justify-center">
              <div className="p-2 rounded-2xl bg-slate-900/60 border border-slate-700/50 shadow-2xl inline-flex gap-3">
                <button
                  onClick={() => setSearchMode('text')}
                  className={`px-8 py-4 rounded-xl font-semibold text-base transition-all duration-300 ${
                    searchMode === 'text'
                      ? 'text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  style={{
                    boxShadow: searchMode === 'text' ? '0 10px 40px rgba(59, 130, 246, 0.4), inset 0 1px 2px rgba(255, 255, 255, 0.2), inset 0 -2px 4px rgba(0, 0, 0, 0.3)' : 'none'
                  }}
                >
                  <FiSearch className="inline-block mr-2 w-5 h-5" />
                  Text Search
                </button>
                <button
                  onClick={() => setSearchMode('image')}
                  className={`px-8 py-4 rounded-xl font-semibold text-base transition-all duration-300 ${
                    searchMode === 'image'
                      ? 'text-white bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  style={{
                    boxShadow: searchMode === 'image' ? '0 10px 40px rgba(236, 72, 153, 0.4), inset 0 1px 2px rgba(255, 255, 255, 0.2), inset 0 -2px 4px rgba(0, 0, 0, 0.3)' : 'none'
                  }}
                >
                  <FiCamera className="inline-block mr-2 w-5 h-5" />
                  Visual Search
                </button>
              </div>
            </div>

            {/* Search Content */}
            {searchMode === 'text' ? (
              <div className="space-y-4">
                <div className="relative flex items-center">
                  <FiSearch className="absolute left-6 w-6 h-6 text-blue-400 z-10" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search for smartphones, laptops, watches..."
                    className="flex-1 w-full px-6 py-5 pl-16 pr-36 bg-slate-800/80 rounded-2xl text-lg text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all border border-slate-700/50 shadow-xl"
                  />
                  <button className="absolute right-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-7 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all whitespace-nowrap">
                    Search
                  </button>
                </div>
                
                {searchQuery && (
                  <div className="flex items-center gap-2 text-sm text-slate-400">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                    AI is ready to search for "{searchQuery}"
                  </div>
                )}

                <div className="flex flex-wrap gap-2">
                  <span className="text-sm text-slate-400">Popular:</span>
                  {['Smartphones', 'Laptops', 'Headphones', 'Watches', 'Cameras'].map((tag) => (
                    <button
                      key={tag}
                      onClick={() => setSearchQuery(tag)}
                      className="px-4 py-2 bg-slate-800/60 text-slate-200 border border-slate-700/50 rounded-full text-sm hover:bg-slate-700/60 hover:border-slate-600 transition-all"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div>
                {uploadedImage ? (
                  <div className="space-y-6">
                    <div className="relative rounded-2xl overflow-hidden border border-slate-700/50">
                      <img src={uploadedImage} alt="Uploaded" className="w-full h-80 object-cover" />
                      <button
                        onClick={() => {
                          setUploadedImage(null)
                          setCategoryHint('')
                          setShowCategoryHint(false)
                        }}
                        className="absolute top-4 right-4 p-3 bg-red-500 text-white rounded-xl shadow-lg hover:bg-red-600 transition-colors"
                      >
                        <FiX className="w-5 h-5" />
                      </button>
                      <div className="absolute bottom-4 left-4 bg-slate-900/90 px-4 py-2 rounded-lg border border-blue-500/30 flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                        <span className="text-sm text-blue-300 font-medium">AI Analyzing...</span>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <button
                        onClick={() => setShowCategoryHint(!showCategoryHint)}
                        className="flex items-center gap-2 text-base text-blue-400 hover:text-blue-300 transition-colors font-medium"
                      >
                        <FiTag className="w-5 h-5" />
                        {showCategoryHint ? 'Hide category hint' : 'Add category hint (Optional)'}
                      </button>
                      
                      {showCategoryHint && (
                        <div className="space-y-4">
                          <select
                            value={categoryHint}
                            onChange={(e) => setCategoryHint(e.target.value)}
                            className="w-full px-5 py-4 bg-slate-800/80 text-white rounded-xl text-base focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all border border-slate-700/50"
                          >
                            <option value="">Select product category...</option>
                            {categoryHints.map((hint) => (
                              <option key={hint} value={hint}>{hint}</option>
                            ))}
                          </select>
                          {categoryHint && (
                            <p className="text-sm text-green-400 flex items-center gap-2">
                              ✓ Great! This helps our AI find better {categoryHint.toLowerCase()} matches
                            </p>
                          )}
                        </div>
                      )}
                    </div>

                    <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-5 rounded-xl font-semibold shadow-xl hover:shadow-2xl transition-all w-full text-lg">
                      Find Similar Products {categoryHint && `in ${categoryHint}`}
                    </button>
                  </div>
                ) : (
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all ${
                      isDragActive ? 'border-purple-500 bg-purple-500/10 scale-[1.02]' : 'border-slate-700 hover:border-purple-400 hover:bg-slate-800/30'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <div className="inline-block mb-6">
                      <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-600/30 to-pink-600/30 border-2 border-purple-500/40 flex items-center justify-center shadow-xl">
                        <FiUpload className="w-12 h-12 text-purple-300" />
                      </div>
                    </div>
                    <p className="text-2xl font-bold text-white mb-3 font-outfit">
                      {isDragActive ? 'Drop your image here' : 'Upload Product Image'}
                    </p>
                    <p className="text-slate-300 mb-6 text-lg">Drag & drop or click to browse</p>
                    <div className="inline-flex items-center gap-2 text-sm text-slate-400 bg-slate-800/60 px-5 py-3 rounded-xl border border-slate-700/50">
                      <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                      AI-Powered • PNG, JPG, JPEG, GIF or WEBP
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
