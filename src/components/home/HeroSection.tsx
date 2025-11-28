'use client'

import { motion } from 'framer-motion'
import { FiArrowRight, FiPlay, FiSmartphone, FiMonitor, FiWatch, FiCamera, FiHeadphones, FiShoppingBag } from 'react-icons/fi'
import Link from 'next/link'

export default function HeroSection() {
  return (
    <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden min-h-screen flex items-center">
      {/* Animated Background Elements - Optimized (2 instead of 3) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.15, 1],
            rotate: [0, 45, 0],
            opacity: [0.35, 0.5, 0.35]
          }}
          transition={{ duration: 30, repeat: Infinity, ease: "linear", repeatType: "loop" }}
          className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-gradient-to-br from-blue-600/40 to-purple-600/40 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.15, 1, 1.15],
            rotate: [45, 0, 45],
            opacity: [0.5, 0.35, 0.5]
          }}
          transition={{ duration: 35, repeat: Infinity, ease: "linear", repeatType: "loop" }}
          className="absolute -bottom-40 -left-40 w-[600px] h-[600px] bg-gradient-to-br from-pink-600/40 via-purple-600/40 to-cyan-600/30 rounded-full blur-3xl"
        />
      </div>

      <div className="max-w-7xl mx-auto w-full relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Text Content */}
          <motion.div
            initial={{ opacity: 0, x: -100, rotateY: -15 }}
            animate={{ opacity: 1, x: 0, rotateY: 0 }}
            transition={{
              duration: 1,
              ease: [0.22, 1, 0.36, 1]
            }}
            className="space-y-8 perspective-1000"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0, rotateZ: -180 }}
              animate={{ opacity: 1, scale: 1, rotateZ: 0 }}
              transition={{
                delay: 0.3,
                duration: 0.8,
                ease: [0.22, 1, 0.36, 1]
              }}
              className="inline-block"
            >
              <span className="glass px-6 py-3 rounded-full text-sm font-medium text-blue-300 shadow-lg border border-blue-400/30">
                ✨ AI-Powered Shopping
              </span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: 0.5,
                duration: 0.8,
                ease: [0.22, 1, 0.36, 1]
              }}
              className="text-5xl md:text-7xl font-bold leading-tight font-outfit text-white"
            >
              Find Your Perfect{' '}
              <motion.span
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{
                  delay: 0.8,
                  duration: 0.6,
                  ease: [0.22, 1, 0.36, 1]
                }}
                className="gradient-text inline-block"
              >
                Product
              </motion.span>
              <br />
              <motion.span
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{
                  delay: 1,
                  duration: 0.6,
                  ease: [0.22, 1, 0.36, 1]
                }}
                className="inline-block"
              >
                in Seconds
              </motion.span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: 1.2,
                duration: 0.6,
                ease: [0.22, 1, 0.36, 1]
              }}
              className="text-xl text-slate-300 leading-relaxed"
            >
              Experience the future of shopping with our advanced AI-powered search.
              Find exactly what you're looking for using text or images.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: 1.4,
                duration: 0.6,
                ease: [0.22, 1, 0.36, 1]
              }}
              className="flex flex-wrap gap-4"
            >
              <Link href="/search">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all inline-flex items-center gap-2 cursor-pointer"
                >
                  Start Searching
                  <FiArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="glass text-slate-200 px-8 py-4 rounded-xl font-medium hover:bg-slate-800/40 transition-all inline-flex items-center gap-2"
              >
                <FiPlay className="w-5 h-5" />
                Watch Demo
              </motion.button>
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: 1.6,
                duration: 0.6,
                ease: [0.22, 1, 0.36, 1]
              }}
              className="grid grid-cols-3 gap-8 pt-8"
            >
              <div>
                <div className="text-3xl font-bold gradient-text font-outfit">1M+</div>
                <div className="text-sm text-slate-200 mt-1 font-medium">Products</div>
              </div>
              <div>
                <div className="text-3xl font-bold gradient-text font-outfit">99%</div>
                <div className="text-sm text-slate-200 mt-1 font-medium">Accuracy</div>
              </div>
              <div>
                <div className="text-3xl font-bold gradient-text font-outfit">&lt;1s</div>
                <div className="text-sm text-slate-200 mt-1 font-medium">Response Time</div>
              </div>
            </motion.div>
          </motion.div>

          {/* Right Column - Galaxy AI Visual */}
          <motion.div
            initial={{ opacity: 0, x: 100, rotateY: 15 }}
            animate={{ opacity: 1, x: 0, rotateY: 0 }}
            transition={{
              duration: 1,
              delay: 0.4,
              ease: [0.22, 1, 0.36, 1]
            }}
            className="relative hidden lg:block"
          >
            <div className="glass-card p-8 rounded-3xl">
              {/* AI Accuracy Card */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.8, duration: 0.6 }}
                className="absolute -top-6 -right-6 z-30 px-6 py-4 rounded-2xl border border-blue-500/40 bg-slate-900/70 backdrop-blur-md shadow-2xl"
              >
                <div className="text-[10px] sm:text-xs text-slate-100 drop-shadow mb-1 font-semibold uppercase tracking-wider">AI Accuracy</div>
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent font-outfit drop-shadow">99.2%</div>
              </motion.div>

              {/* Main Visual - Galaxy AI Style */}
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex items-center justify-center relative overflow-hidden">
                
                {/* Deep radial gradient background - single elegant layer */}
                <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-slate-950/60" />
                
                {/* Main cosmic glow - optimized */}
                <motion.div
                  animate={{
                    scale: [1, 1.15, 1],
                    opacity: [0.5, 0.65, 0.5],
                  }}
                  transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "easeInOut",
                    repeatType: "loop"
                  }}
                  className="absolute w-[340px] h-[340px] rounded-full"
                  style={{
                    background: 'radial-gradient(circle, rgba(109, 40, 217, 0.35) 0%, rgba(139, 92, 246, 0.25) 30%, rgba(168, 85, 247, 0.15) 50%, transparent 70%)',
                    filter: 'blur(30px)',
                  }}
                />

                {/* Subtle nebula swirl - optimized slower rotation */}
                <motion.div
                  animate={{
                    rotate: 360,
                  }}
                  transition={{
                    duration: 120,
                    repeat: Infinity,
                    ease: "linear",
                    repeatType: "loop"
                  }}
                  className="absolute w-[380px] h-[380px] rounded-full opacity-15"
                  style={{
                    background: 'conic-gradient(from 0deg, transparent, rgba(139, 92, 246, 0.25), transparent 50%, rgba(236, 72, 153, 0.2), transparent)',
                    filter: 'blur(25px)',
                  }}
                />

                {/* Fine starlight particles - optimized (4 instead of 8) */}
                {[...Array(4)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-[2px] h-[2px] rounded-full"
                    style={{
                      left: `${25 + i * 15}%`,
                      top: `${30 + i * 10}%`,
                      background: i % 2 === 0 ? 'rgba(255, 255, 255, 0.6)' : 'rgba(168, 85, 247, 0.5)',
                    }}
                    animate={{
                      opacity: [0.3, 0.8, 0.3],
                      scale: [1, 1.4, 1],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      delay: i * 0.7,
                      ease: "easeInOut",
                      repeatType: "loop"
                    }}
                  />
                ))}

                {/* Minimal orbital rings - optimized without willChange */}
                <motion.div
                  className="absolute w-[300px] h-[300px] rounded-full border border-purple-400/[0.7] z-20"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 100, repeat: Infinity, ease: "linear", repeatType: "loop" }}
                />
                <motion.div
                  className="absolute w-[340px] h-[340px] rounded-full border border-indigo-400/[0.7] z-20"
                  animate={{ rotate: -360 }}
                  transition={{ duration: 120, repeat: Infinity, ease: "linear", repeatType: "loop" }}
                />

                {/* Connection Lines - thin minimal light rays with glow */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  <defs>
                    <linearGradient id="galaxyLineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.12" />
                      <stop offset="50%" stopColor="#a855f7" stopOpacity="0.18" />
                      <stop offset="100%" stopColor="#ec4899" stopOpacity="0.12" />
                    </linearGradient>
                    <filter id="lineGlow">
                      <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>
                  {[0, 60, 120, 180, 240, 300].map((angle, index) => {
                    const centerX = 50;
                    const centerY = 50;
                    const radius = 36;
                    const endX = centerX + Math.cos((angle * Math.PI) / 180) * radius;
                    const endY = centerY + Math.sin((angle * Math.PI) / 180) * radius;
                    
                    return (
                      <motion.line
                        key={index}
                        x1={`${centerX}%`}
                        y1={`${centerY}%`}
                        x2={`${endX}%`}
                        y2={`${endY}%`}
                        stroke="url(#galaxyLineGradient)"
                        strokeWidth="0.8"
                        filter="url(#lineGlow)"
                        initial={{ pathLength: 0, opacity: 0 }}
                        animate={{ pathLength: 1, opacity: 1 }}
                        transition={{ delay: 0.8 + index * 0.1, duration: 0.7, ease: "easeOut" }}
                      />
                    );
                  })}
                </svg>

                {/* Floating Product Icons - evenly distributed, consistent scale */}
                {[
                  { Icon: FiSmartphone, angle: 0, color: 'from-blue-500 to-cyan-500', glowColor: 'rgba(59, 130, 246, 0.3)', label: 'Phones' },
                  { Icon: FiMonitor, angle: 60, color: 'from-purple-500 to-pink-500', glowColor: 'rgba(168, 85, 247, 0.3)', label: 'Laptops' },
                  { Icon: FiWatch, angle: 120, color: 'from-green-500 to-emerald-500', glowColor: 'rgba(34, 197, 94, 0.3)', label: 'Watches' },
                  { Icon: FiCamera, angle: 180, color: 'from-orange-500 to-red-500', glowColor: 'rgba(249, 115, 22, 0.3)', label: 'Cameras' },
                  { Icon: FiHeadphones, angle: 240, color: 'from-yellow-500 to-orange-500', glowColor: 'rgba(234, 179, 8, 0.3)', label: 'Audio' },
                  { Icon: FiShoppingBag, angle: 300, color: 'from-pink-500 to-rose-500', glowColor: 'rgba(236, 72, 153, 0.3)', label: 'Fashion' },
                ].map((item, index) => {
                  const radius = 140;
                  const angleInRadians = (item.angle * Math.PI) / 180;
                  const x = Math.cos(angleInRadians) * radius;
                  const y = Math.sin(angleInRadians) * radius;
                  
                  return (
                    <motion.div
                      key={index}
                      className="absolute z-30"
                      style={{
                        left: '50%',
                        top: '50%',
                      }}
                      initial={{ opacity: 0, scale: 0, x: -32, y: -32 }}
                      animate={{ 
                        opacity: 1, 
                        scale: 1,
                        x: x - 32,
                        y: y - 32,
                      }}
                      transition={{
                        delay: 0.5 + index * 0.12,
                        duration: 0.9,
                        type: "spring",
                        stiffness: 140,
                        damping: 18
                      }}
                    >
                      <motion.div
                        animate={{
                          y: [-5, 5, -5],
                        }}
                        transition={{
                          duration: 6,
                          repeat: Infinity,
                          delay: index * 0.8,
                          ease: "easeInOut",
                          repeatType: "loop"
                        }}
                      >
                        <motion.div
                          whileHover={{ 
                            scale: 1.15,
                            transition: { duration: 0.3, ease: "easeOut" }
                          }}
                          className="relative group cursor-pointer"
                        >
                          {/* Gentle icon glow - NON-overlapping */}
                          <motion.div
                            className="absolute -inset-2 rounded-2xl blur-lg opacity-50"
                            style={{
                              background: item.glowColor,
                            }}
                            animate={{
                              scale: [1, 1.15, 1],
                              opacity: [0.4, 0.6, 0.4],
                            }}
                            transition={{
                              duration: 3.5,
                              repeat: Infinity,
                              delay: index * 0.4,
                              ease: "easeInOut",
                              repeatType: "loop"
                            }}
                          />
                          
                          <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${item.color} p-3.5 flex items-center justify-center shadow-2xl border border-white/10 relative z-10 backdrop-blur-sm`}
                            style={{
                              boxShadow: `0 8px 32px ${item.glowColor}, inset 0 1px 2px rgba(255, 255, 255, 0.15)`,
                            }}
                          >
                            <item.Icon className="w-8 h-8 text-white drop-shadow-lg" />
                          </div>
                          
                          {/* Tooltip */}
                          <div className="absolute -bottom-10 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap pointer-events-none z-50">
                            <span className="text-xs font-semibold text-white bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-purple-400/30 shadow-xl">
                              {item.label}
                            </span>
                          </div>
                        </motion.div>
                      </motion.div>
                    </motion.div>
                  );
                })}

                {/* Center AI Badge - Galaxy AI Style with soft light aura */}
                <motion.div
                  className="absolute z-10"
                  style={{
                    left: '38%',
                    top: '38%',
                    transform: 'translate(-50%, -50%)'
                  }}
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ 
                    scale: 1,
                    opacity: 1,
                  }}
                  transition={{
                    delay: 0.5,
                    duration: 1.4,
                    ease: [0.16, 1, 0.3, 1]
                  }}
                >
                  <div className="relative w-32 h-32">
                    {/* Glass lens effect - premium 3D */}
                    <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/8 to-transparent blur-sm" />
                    
                    {/* Soft light aura around AI - enhanced glow (optimized) */}
                    <motion.div
                      className="absolute inset-0 rounded-full"
                      style={{
                        background: 'radial-gradient(circle, rgba(168, 85, 247, 0.7) 0%, rgba(139, 92, 246, 0.5) 40%, transparent 70%)',
                        filter: 'blur(24px)',
                      }}
                      animate={{
                        scale: [1, 1.15, 1],
                        opacity: [0.7, 0.85, 0.7],
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: [0.4, 0, 0.6, 1],
                        repeatType: "loop"
                      }}
                    />
                    
                    {/* Rotating ring - enhanced with blur */}
                    <motion.div
                      className="absolute inset-0 rounded-full"
                      style={{
                        background: 'conic-gradient(from 0deg, transparent, #3b82f6, #8b5cf6, transparent)',
                        filter: 'blur(3px)',
                        opacity: 0.6
                      }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 10, repeat: Infinity, ease: "linear", repeatType: "loop" }}
                    />
                    
                    {/* AI Badge with premium 3D depth */}
                    <div className="absolute inset-2 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center shadow-2xl border-2 border-slate-900/50 backdrop-blur-sm"
                      style={{
                        boxShadow: '0 25px 80px rgba(59, 130, 246, 0.5), 0 0 100px rgba(139, 92, 246, 0.4), inset 0 -10px 30px rgba(0,0,0,0.4), inset 0 3px 15px rgba(255,255,255,0.2), inset 0 0 40px rgba(139, 92, 246, 0.3)',
                      }}
                    >
                      {/* Specular highlight - premium glass effect */}
                      <div className="absolute top-3 left-5 w-10 h-10 rounded-full bg-white/25 blur-lg" />
                      <div className="absolute top-2 left-4 w-6 h-6 rounded-full bg-white/35 blur-sm" />
                      
                      <motion.div 
                        className="text-white font-outfit font-bold text-4xl tracking-wide relative z-10"
                        style={{
                          textShadow: '0 3px 12px rgba(0,0,0,0.6), 0 0 40px rgba(255,255,255,0.4)',
                        }}
                        animate={{ 
                          textShadow: [
                            "0 3px 12px rgba(0,0,0,0.6), 0 0 40px rgba(59, 130, 246, 1)",
                            "0 3px 12px rgba(0,0,0,0.6), 0 0 50px rgba(139, 92, 246, 1.2)",
                            "0 3px 12px rgba(0,0,0,0.6), 0 0 40px rgba(236, 72, 153, 1)",
                            "0 3px 12px rgba(0,0,0,0.6), 0 0 40px rgba(59, 130, 246, 1)",
                          ]
                        }}
                        transition={{ duration: 8, repeat: Infinity, ease: "linear", repeatType: "loop" }}
                      >
                        AI
                      </motion.div>
                    </div>

                    {/* Enhanced pulse rings with glow (optimized) */}
                    <motion.div
                      className="absolute inset-0 rounded-full border-2 border-purple-400/40"
                      style={{
                        boxShadow: '0 0 30px rgba(139, 92, 246, 0.8)',
                      }}
                      animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
                      transition={{ duration: 3, repeat: Infinity, ease: [0.4, 0, 0.2, 1], repeatType: "loop" }}
                    />
                    <motion.div
                      className="absolute inset-0 rounded-full border-2 border-blue-400/40"
                      style={{
                        boxShadow: '0 0 30px rgba(59, 130, 246, 0.8)',
                      }}
                      animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
                      transition={{ duration: 3, repeat: Infinity, delay: 1.5, ease: [0.4, 0, 0.2, 1], repeatType: "loop" }}
                    />
                    
                    {/* Micro star particles around orb (optimized) */}
                    {[...Array(8)].map((_, i) => (
                      <motion.div
                        key={i}
                        className="absolute w-1.5 h-1.5 rounded-full bg-blue-300"
                        style={{
                          top: `${50 + Math.cos((i * Math.PI) / 4) * 65}%`,
                          left: `${50 + Math.sin((i * Math.PI) / 4) * 65}%`,
                          boxShadow: '0 0 10px rgba(59, 130, 246, 1), 0 0 20px rgba(139, 92, 246, 0.6)',
                        }}
                        animate={{
                          scale: [0.8, 1.2, 0.8],
                          opacity: [0.3, 0.8, 0.3],
                        }}
                        transition={{
                          duration: 3,
                          repeat: Infinity,
                          delay: i * 0.375,
                          ease: [0.4, 0, 0.6, 1],
                          repeatType: "loop"
                        }}
                      />
                    ))}
                  </div>
                </motion.div>
              </div>

              {/* Search Speed Card */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 2, duration: 0.6 }}
                className="absolute -bottom-6 -left-6 glass-card px-6 py-4 rounded-2xl border border-purple-500/30"
              >
                <div className="text-xs text-white mb-1 font-semibold uppercase tracking-wide">Search Speed</div>
                <div className="text-3xl font-bold gradient-text font-outfit">0.8s</div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
