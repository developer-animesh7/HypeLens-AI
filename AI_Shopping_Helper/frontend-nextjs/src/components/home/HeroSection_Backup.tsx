'use client'

import { motion } from 'framer-motion'
import { FiArrowRight, FiPlay, FiSmartphone, FiMonitor, FiWatch, FiCamera, FiHeadphones, FiShoppingBag } from 'react-icons/fi'

export default function HeroSection() {
  return (
    <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden min-h-screen flex items-center">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 90, 0],
            opacity: [0.4, 0.6, 0.4]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-gradient-to-br from-blue-600/40 to-purple-600/40 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.2, 1, 1.2],
            rotate: [90, 0, 90],
            opacity: [0.6, 0.4, 0.6]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute -bottom-40 -left-40 w-[600px] h-[600px] bg-gradient-to-br from-pink-600/40 to-purple-600/40 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-br from-cyan-600/30 to-blue-600/30 rounded-full blur-3xl"
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
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all inline-flex items-center gap-2"
              >
                Start Searching
                <FiArrowRight className="w-5 h-5" />
              </motion.button>
              
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

          {/* Right Column - Visual */}
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
                className="absolute -top-6 -right-6 glass-card px-6 py-4 rounded-2xl border border-blue-500/30"
              >
                <div className="text-xs text-white mb-1 font-semibold uppercase tracking-wide">AI Accuracy</div>
                <div className="text-3xl font-bold gradient-text font-outfit">99.2%</div>
              </motion.div>

              {/* Main Visual */}
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center relative overflow-hidden">
                {/* Background Glow */}
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, 360],
                  }}
                  transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                  className="absolute w-48 h-48 rounded-full bg-gradient-to-br from-blue-600/20 to-purple-600/20 blur-2xl"
                />

                {/* Galaxy swirl behind AI (will be enhanced) */}
                <motion.div
                  className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-0 rounded-full"
                  style={{ width: 260, height: 260, overflow: 'hidden' }}
                  animate={{ rotate: 360 }}
                  transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
                >
                  {/* Swirl layers */}
                  <div
                    className="absolute inset-0 rounded-full blur-sm"
                    style={{
                      backgroundImage:
                        'radial-gradient(circle at 50% 50%, rgba(255,255,255,0.35) 0%, rgba(99,102,241,0.18) 15%, rgba(168,85,247,0.15) 30%, rgba(0,0,0,0) 60%), conic-gradient(from 0deg, rgba(59,130,246,0.18), rgba(168,85,247,0.18), rgba(236,72,153,0.18), rgba(59,130,246,0.18))',
                      filter: 'drop-shadow(0 0 14px rgba(99,102,241,0.25))',
                    }}
                  />
                  <div
                    className="absolute inset-0 rounded-full mix-blend-screen"
                    style={{
                      backgroundImage:
                        'radial-gradient(circle at 60% 45%, rgba(99,102,241,0.22), transparent 40%), radial-gradient(circle at 40% 55%, rgba(236,72,153,0.2), transparent 45%)',
                    }}
                  />
                  {/* Tiny star particles */}
                  {[...Array(18)].map((_, i) => (
                    <motion.span
                      key={i}
                      className="absolute block rounded-full"
                      style={{
                        width: 2,
                        height: 2,
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        background:
                          i % 3 === 0
                            ? 'rgba(255,255,255,0.9)'
                            : i % 3 === 1
                            ? 'rgba(99,102,241,0.9)'
                            : 'rgba(236,72,153,0.9)',
                      }}
                      animate={{ opacity: [0.2, 1, 0.2], scale: [0.8, 1.4, 0.8] }}
                      transition={{ duration: 2 + (i % 5) * 0.3, repeat: Infinity, delay: i * 0.1 }}
                    />
                  ))}
                </motion.div>

                {/* Single subtle orbital ring for balance */}
                <motion.div
                  className="absolute w-[360px] h-[360px] rounded-full border border-purple-500/15"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 80, repeat: Infinity, ease: "linear" }}
                />

                {/* Connection Lines */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  <defs>
                    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.4" />
                      <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.4" />
                      <stop offset="100%" stopColor="#ec4899" stopOpacity="0.4" />
                    </linearGradient>
                  </defs>
                  {[0, 60, 120, 180, 240, 300].map((angle, index) => {
                    const centerX = 50; // percentage
                    const centerY = 50; // percentage
                    const radius = 42; // percentage (wider reach)
                    const endX = centerX + Math.cos((angle * Math.PI) / 180) * radius;
                    const endY = centerY + Math.sin((angle * Math.PI) / 180) * radius;
                    
                    return (
                      <motion.line
                        key={index}
                        x1={`${centerX}%`}
                        y1={`${centerY}%`}
                        x2={`${endX}%`}
                        y2={`${endY}%`}
                        stroke="url(#lineGradient)"
                        strokeWidth="2"
                        initial={{ pathLength: 0, opacity: 0 }}
                        animate={{ pathLength: 1, opacity: 1 }}
                        transition={{ delay: 0.8 + index * 0.1, duration: 0.6, ease: "easeOut" }}
                      />
                    );
                  })}
                </svg>

                {/* Floating Product Icons (smaller, more spaced) */}
                {[
                  { Icon: FiSmartphone, angle: 0, color: 'from-blue-500 to-cyan-500', label: 'Phones' },
                  { Icon: FiMonitor, angle: 60, color: 'from-purple-500 to-pink-500', label: 'Laptops' },
                  { Icon: FiWatch, angle: 120, color: 'from-green-500 to-emerald-500', label: 'Watches' },
                  { Icon: FiCamera, angle: 180, color: 'from-orange-500 to-red-500', label: 'Cameras' },
                  { Icon: FiHeadphones, angle: 240, color: 'from-yellow-500 to-orange-500', label: 'Audio' },
                  { Icon: FiShoppingBag, angle: 300, color: 'from-pink-500 to-rose-500', label: 'Fashion' },
                ].map((item, index) => {
                  // Calculate position in circular orbit
                  const radius = 185; // increased radius for more negative space
                  const angleInRadians = (item.angle * Math.PI) / 180;
                  const x = Math.cos(angleInRadians) * radius;
                  const y = Math.sin(angleInRadians) * radius;
                  
                  return (
                    <motion.div
                      key={index}
                      className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10"
                      initial={{ opacity: 0, scale: 0, x: 0, y: 0 }}
                      animate={{ 
                        opacity: 1, 
                        scale: 1,
                        x: x,
                        y: y,
                      }}
                      transition={{
                        delay: 0.5 + index * 0.1,
                        duration: 0.6,
                        type: "spring",
                        stiffness: 200
                      }}
                    >
                      <motion.div
                        animate={{
                          y: [-8, 8, -8],
                        }}
                        transition={{
                          duration: 3,
                          repeat: Infinity,
                          delay: index * 0.3,
                          ease: "easeInOut",
                        }}
                      >
                        <motion.div
                          whileHover={{ 
                            scale: 1.3, 
                            rotate: 360,
                            transition: { duration: 0.5 }
                          }}
                          className="relative group cursor-pointer"
                        >
                          <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${item.color} p-3 flex items-center justify-center shadow-lg border border-white/10 relative z-10 backdrop-blur-sm`}>
                            <item.Icon className="w-7 h-7 text-white" />
                          </div>
                          
                          {/* Tooltip */}
                          <div className="absolute -bottom-9 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap pointer-events-none z-50">
                            <span className="text-xs font-semibold text-white bg-slate-800/95 px-3 py-1.5 rounded-lg border border-white/20 shadow-lg">
                              {item.label}
                            </span>
                          </div>

                          {/* Glow effect on hover */}
                          <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${item.color} opacity-0 group-hover:opacity-60 blur-xl transition-opacity duration-300 -z-10`} />
                          
                          {/* Floating particles */}
                          <motion.div
                            className={`absolute w-2 h-2 rounded-full bg-gradient-to-br ${item.color}`}
                            animate={{
                              x: [0, 15, 0],
                              y: [0, -15, 0],
                              opacity: [0, 1, 0],
                            }}
                            transition={{
                              duration: 2.5,
                              repeat: Infinity,
                              delay: index * 0.4,
                            }}
                            style={{ top: -5, left: -5 }}
                          />
                        </motion.div>
                      </motion.div>
                    </motion.div>
                  );
                })}

                {/* Center AI core – single ring + clear label */}
                <motion.div
                  className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20"
                  initial={{ opacity: 0, scale: 0.85 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4, duration: 0.6, ease: 'easeOut' }}
                >
                  <div className="relative flex items-center justify-center">
                    {/* Single smooth glow ring */}
                    <motion.div
                      className="absolute w-56 h-56 rounded-full opacity-70"
                      style={{
                        background:
                          'conic-gradient(from 0deg, rgba(59,130,246,0), rgba(59,130,246,0.5), rgba(168,85,247,0.45), rgba(236,72,153,0.5), rgba(59,130,246,0))',
                        maskImage: 'radial-gradient(circle at center, transparent 58%, black 60%)',
                        WebkitMaskImage: 'radial-gradient(circle at center, transparent 58%, black 60%)',
                        filter: 'blur(8px)'
                      }}
                      animate={{ rotate: 360 }}
                      transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                    />
                    {/* Soft inner glow for depth */}
                    <div
                      className="absolute w-40 h-40 rounded-full"
                      style={{
                        background:
                          'radial-gradient(circle at center, rgba(255,255,255,0.85) 0%, rgba(99,102,241,0.45) 30%, rgba(0,0,0,0) 65%)',
                        filter: 'blur(6px)'
                      }}
                    />
                    {/* Clear centered AI text */}
                    <span className="relative font-outfit font-extrabold text-6xl text-white tracking-wide drop-shadow-[0_0_18px_rgba(99,102,241,0.6)]">
                      AI
                    </span>
                  </div>
                </motion.div>
              </div>

              {/* Search Speed Card */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 2, duration: 0.6 }}
                className="absolute -top-6 -right-6 z-30 px-6 py-4 rounded-2xl border border-blue-500/40 bg-slate-900/70 backdrop-blur-md shadow-2xl"
              >
                <div className="text-[10px] sm:text-xs text-slate-100 drop-shadow mb-1 font-semibold uppercase tracking-wider">AI Accuracy</div>
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent font-outfit drop-shadow">99.2%</div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
