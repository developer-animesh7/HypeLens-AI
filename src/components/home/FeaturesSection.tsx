'use client'

import { motion } from 'framer-motion'
import { FiZap, FiTarget, FiTrendingUp, FiShield, FiClock, FiAward } from 'react-icons/fi'

export default function FeaturesSection() {
  const features = [
    {
      icon: FiZap,
      title: 'Lightning Fast',
      description: 'Get search results in under 1 second with our optimized AI algorithms.',
      gradient: 'from-yellow-400 to-orange-500',
    },
    {
      icon: FiTarget,
      title: 'Precise Matching',
      description: 'Advanced AI ensures you find exactly what you\'re looking for.',
      gradient: 'from-blue-400 to-cyan-500',
    },
    {
      icon: FiTrendingUp,
      title: 'Smart Recommendations',
      description: 'Discover products you\'ll love based on your preferences.',
      gradient: 'from-green-400 to-emerald-500',
    },
    {
      icon: FiShield,
      title: 'Secure & Private',
      description: 'Your data is encrypted and never shared with third parties.',
      gradient: 'from-purple-400 to-pink-500',
    },
    {
      icon: FiClock,
      title: 'Real-time Updates',
      description: 'Always see the latest products and prices from multiple sources.',
      gradient: 'from-red-400 to-rose-500',
    },
    {
      icon: FiAward,
      title: 'Best Deals',
      description: 'Compare prices instantly to find the best deals available.',
      gradient: 'from-indigo-400 to-violet-500',
    },
  ]

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16 space-y-4"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white font-outfit">
            Why Choose <span className="gradient-text">HypeLens AI</span>
          </h2>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Experience the next generation of product discovery with cutting-edge AI technology
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -8 }}
              className="glass-card p-8 space-y-4 group cursor-pointer"
            >
              {/* Icon */}
              <motion.div
                whileHover={{ rotate: 360, scale: 1.1 }}
                transition={{ duration: 0.6 }}
                className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center shadow-lg`}
              >
                <feature.icon className="w-7 h-7 text-white" />
              </motion.div>

              {/* Content */}
              <div className="space-y-2">
                <h3 className="text-xl font-bold text-white group-hover:gradient-text transition-all">
                  {feature.title}
                </h3>
                <p className="text-slate-300 leading-relaxed">
                  {feature.description}
                </p>
              </div>

              {/* Hover Effect Line */}
              <motion.div
                initial={{ width: 0 }}
                whileHover={{ width: '100%' }}
                className={`h-1 bg-gradient-to-r ${feature.gradient} rounded-full`}
              />
            </motion.div>
          ))}
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-20 text-center glass-card p-12"
        >
          <h3 className="text-3xl md:text-4xl font-bold mb-4 text-white font-outfit">
            Ready to revolutionize your shopping?
          </h3>
          <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
            Join thousands of users who are already discovering products faster and smarter
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all text-lg"
          >
            Get Started For Free
          </motion.button>
        </motion.div>
      </div>
    </section>
  )
}
