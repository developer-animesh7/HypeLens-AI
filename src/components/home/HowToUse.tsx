'use client'

import { motion } from 'framer-motion'
import { FiSearch, FiCamera, FiCheckCircle, FiZap } from 'react-icons/fi'

const steps = [
  {
    icon: FiSearch,
    title: 'Text Search',
    description: 'Type product name or paste a product link',
    color: 'from-blue-500 to-cyan-500',
    delay: 0.2
  },
  {
    icon: FiCamera,
    title: 'Visual Search',
    description: 'Upload or drag & drop product image',
    color: 'from-purple-500 to-pink-500',
    delay: 0.3
  },
  {
    icon: FiZap,
    title: 'AI Analysis',
    description: 'Our AI finds similar products instantly',
    color: 'from-orange-500 to-red-500',
    delay: 0.4
  },
  {
    icon: FiCheckCircle,
    title: 'Compare & Save',
    description: 'Get best prices and alternatives',
    color: 'from-green-500 to-emerald-500',
    delay: 0.5
  }
]

export default function HowToUse() {
  return (
    <div className="mt-16 mb-8">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className="text-center mb-12"
      >
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          <span className="gradient-text font-outfit">How It Works</span>
        </h2>
        <p className="text-slate-300 text-lg">
          Find your perfect product in just a few simple steps
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 50, rotateX: -15 }}
            whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
            viewport={{ once: true }}
            transition={{
              duration: 0.7,
              delay: step.delay,
              ease: [0.22, 1, 0.36, 1]
            }}
            whileHover={{
              y: -10,
              rotateY: 5,
              transition: { duration: 0.3 }
            }}
            className="group perspective-1000"
          >
            <div className="glass-card p-6 h-full preserve-3d">
              {/* Step Number */}
              <div className="flex items-start justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <step.icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-3xl font-bold text-slate-600 font-outfit">
                  {index + 1}
                </span>
              </div>

              {/* Content */}
              <h3 className="text-xl font-bold mb-2 text-white font-outfit">
                {step.title}
              </h3>
              <p className="text-slate-300">
                {step.description}
              </p>

              {/* Decorative Element */}
              <motion.div
                className={`mt-4 h-1 rounded-full bg-gradient-to-r ${step.color}`}
                initial={{ width: 0 }}
                whileInView={{ width: '100%' }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: step.delay + 0.2 }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Connection Lines (Desktop only) */}
      <div className="hidden lg:block relative -mt-32 pointer-events-none">
        <svg className="w-full h-32" viewBox="0 0 1000 100">
          {[0, 1, 2].map((i) => (
            <motion.path
              key={i}
              d={`M ${250 + i * 250} 0 Q ${250 + i * 250 + 125} 50 ${250 + i * 250 + 250} 0`}
              stroke="url(#gradient)"
              strokeWidth="2"
              fill="none"
              strokeDasharray="5,5"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 0.3 }}
              viewport={{ once: true }}
              transition={{ duration: 1.5, delay: 0.5 + i * 0.2 }}
            />
          ))}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="50%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#ec4899" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>
  )
}
