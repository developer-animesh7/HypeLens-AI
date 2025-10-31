'use client';

import { useState, useRef } from 'react';
import { ProductAnalysis } from '@/types/product';

interface ImageSearchUploadProps {
  onResults: (results: any) => void;
  disabled?: boolean;
  searchSource?: 'auto' | 'local' | 'web';
}

export function ImageSearchUpload({ onResults, disabled = false, searchSource = 'auto' }: ImageSearchUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [queryText, setQueryText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file (JPEG, PNG, etc.)');
      return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('Image file is too large. Please select a file under 10MB.');
      return;
    }
    
    // Show preview and store file (don't search yet)
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    setSelectedFile(file);
  };

  const handleSearch = async () => {
    if (!selectedFile) {
      alert('Please select an image first');
      return;
    }
    
    // Strongly encourage query text for better results
    if (!queryText.trim()) {
      const confirmed = confirm(
        '⚠️ No product name entered!\n\n' +
        'For BEST results, please type the product name (e.g., "Samsung S24", "iPhone 16").\n\n' +
        '❌ Without text: May show mixed categories (cameras, headphones, etc.)\n' +
        '✅ With text: 80% more accurate - finds exact product!\n\n' +
        'Click OK to search anyway, or Cancel to add product name.'
      );
      if (!confirmed) {
        return;
      }
    }
    
    setIsLoading(true);
    try {
  const formData = new FormData();
  formData.append('file', selectedFile);
  formData.append('top_k', '10');
  formData.append('source', searchSource);
  
  // Add query text if provided (optional but improves results)
  if (queryText.trim()) {
    formData.append('query_text', queryText.trim());
  }

      // Determine API base URL with fallback (handles dynamic backend port 8000/8001)
      const envBase = process.env.NEXT_PUBLIC_API_BASE?.trim();
      const bases = Array.from(new Set([
        envBase || 'http://localhost:8000',
        'http://localhost:8001',
      ].filter(Boolean)));

      let lastError: any = null;
      for (const base of bases) {
        try {
          // Use hybrid search endpoint which supports ViT-L/14 (768-dim) model
          const response = await fetch(`${base}/api/hybrid/hybrid_search`, {
            method: 'POST',
            body: formData,
          });
          if (response.ok) {
            const data = await response.json();
            onResults(data);
            lastError = null;
            break;
          } else {
            lastError = new Error(`Search failed: ${response.status}`);
          }
        } catch (err) {
          lastError = err;
        }
      }
      if (lastError) {
        throw lastError;
      }
      
    } catch (error) {
  console.error('Image search error:', error);
  alert('Failed to search for similar products. Please ensure the backend is running and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (!disabled) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  return (
    <div className="max-w-3xl mx-auto mb-8">
      <div className="relative bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border-2 border-white/20 p-10 overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5 animate-gradient"></div>
        
        <div className="relative z-10">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-extrabold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-3 animate-fade-in">
              🖼️ Search by Image
            </h3>
            <p className="text-gray-600 text-lg">
              Upload an image to find similar products using AI image recognition
            </p>
          </div>
          
          {/* Optional Query Text Input with Hint */}
          <div className="mb-6">
            <label className="block text-sm font-bold text-gray-700 mb-2">
              Product Name (Highly Recommended) 
              <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="text"
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Type product name: 'Samsung S24', 'iPhone 16', 'MacBook Air' etc."
                className="w-full px-6 py-4 pr-12 text-base rounded-2xl border-2 border-blue-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 bg-white shadow-sm placeholder-gray-400"
                disabled={disabled || isLoading}
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                <span className="text-2xl">🔍</span>
              </div>
            </div>
            <div className="mt-3 p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded-r-lg">
              <p className="text-sm text-yellow-800 flex items-start space-x-2">
                <svg className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>
                  <strong>Important:</strong> Adding product name improves accuracy by 80%! 
                  Without it, you may see mixed categories (cameras, headphones for phone searches).
                </span>
              </p>
            </div>
          </div>
          
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={handleClick}
            className={`
              group relative border-4 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-500 transform
              ${isDragging ? 'border-blue-500 bg-blue-50 scale-105 shadow-2xl' : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50/50 hover:scale-102'}
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
              ${isLoading ? 'pointer-events-none' : ''}
            `}
          >
            {/* Animated border glow on hover */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500"></div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
              disabled={disabled}
              aria-label="Upload image file for product search"
            />
            
            {previewUrl && !isLoading ? (
              <div className="space-y-6 animate-scale-in">
                <div className="relative inline-block">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-w-full max-h-64 mx-auto rounded-2xl shadow-2xl border-4 border-white transform transition-transform duration-500 hover:scale-105"
                  />
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-t from-black/20 to-transparent"></div>
                </div>
                <p className="text-sm text-gray-500 font-medium flex items-center justify-center space-x-2">
                  <span className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  <span>Click to upload a different image</span>
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {isLoading ? (
                  <div className="flex flex-col items-center space-y-4">
                    <div className="relative">
                      <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                      <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-purple-600 rounded-full animate-spin" style={{animationDuration: '1.5s', animationDirection: 'reverse'}}></div>
                    </div>
                    <p className="text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                      Searching for similar products...
                    </p>
                    <p className="text-sm text-gray-500">AI is analyzing your image</p>
                  </div>
                ) : (
                  <>
                    <div className="relative inline-block">
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-3xl blur-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-500"></div>
                      <svg
                        className="relative mx-auto h-24 w-24 text-gray-400 group-hover:text-blue-500 transition-all duration-500 transform group-hover:scale-110 group-hover:rotate-3"
                        stroke="currentColor"
                        fill="none"
                        viewBox="0 0 48 48"
                      >
                        <path
                          d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                          strokeWidth={2}
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </div>
                    <div>
                      <p className="text-base text-gray-700 mb-2">
                        <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 text-lg">Click to upload</span>
                        <span className="text-gray-500"> or drag and drop</span>
                      </p>
                      <p className="text-sm text-gray-500 font-medium">PNG, JPG, GIF up to 10MB</p>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        
        {previewUrl && (
          <div className="mt-6 space-y-3">
            <button
              onClick={handleSearch}
              disabled={isLoading}
              className={`w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold text-lg rounded-xl shadow-lg transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <span className="text-2xl">🔍</span>
              <span>{isLoading ? 'Searching...' : 'Search Similar Products'}</span>
            </button>
            
            <button
              onClick={() => {
                setPreviewUrl(null);
                setSelectedFile(null);
                setQueryText('');
                if (fileInputRef.current) {
                  fileInputRef.current.value = '';
                }
              }}
              disabled={isLoading}
              className="w-full px-4 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-xl shadow-lg transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              🗑️ Clear & Start Over
            </button>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
