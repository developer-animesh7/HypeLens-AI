'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { FiMail, FiPhone, FiMapPin, FiLinkedin, FiTwitter, FiGithub, FiInstagram } from 'react-icons/fi'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    product: [
      { label: 'Features', href: '#features' },
      { label: 'How It Works', href: '#how-it-works' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'API', href: '#api' },
    ],
    company: [
      { label: 'About Us', href: '#about' },
      { label: 'Careers', href: '#careers' },
      { label: 'Blog', href: '#blog' },
      { label: 'Press Kit', href: '#press' },
    ],
    support: [
      { label: 'Help Center', href: '#help' },
      { label: 'Documentation', href: '#docs' },
      { label: 'Contact Us', href: '#contact' },
      { label: 'Status', href: '#status' },
    ],
    legal: [
      { label: 'Privacy Policy', href: '#privacy' },
      { label: 'Terms of Service', href: '#terms' },
      { label: 'Cookie Policy', href: '#cookies' },
      { label: 'Licenses', href: '#licenses' },
    ],
  }

  const socialLinks = [
    { icon: FiLinkedin, href: '#', label: 'LinkedIn' },
    { icon: FiTwitter, href: '#', label: 'Twitter' },
    { icon: FiGithub, href: '#', label: 'GitHub' },
    { icon: FiInstagram, href: '#', label: 'Instagram' },
  ]

  return (
    <footer className="relative bg-slate-950 border-t border-slate-800 pt-20 pb-10">
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-900/50 to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-12 mb-16">
          {/* Company Info */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="space-y-6"
            >
              {/* Logo */}
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-xl">HL</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold gradient-text font-outfit">HypeLens</h3>
                  <p className="text-xs text-slate-400">Pvt Ltd</p>
                </div>
              </div>

              <p className="text-slate-400 text-sm leading-relaxed">
                Revolutionizing online shopping with cutting-edge AI technology. 
                Find the perfect products faster with our intelligent search and price comparison platform.
              </p>

              {/* Contact Info */}
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm text-slate-400">
                  <FiMail className="w-4 h-4 text-blue-400" />
                  <a href="mailto:contact@hypelens.com" className="hover:text-blue-400 transition-colors">
                    contact@hypelens.com
                  </a>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-400">
                  <FiPhone className="w-4 h-4 text-blue-400" />
                  <a href="tel:+1234567890" className="hover:text-blue-400 transition-colors">
                    +1 (234) 567-890
                  </a>
                </div>
                <div className="flex items-center gap-3 text-sm text-slate-400">
                  <FiMapPin className="w-4 h-4 text-blue-400" />
                  <span>123 Innovation Street, Tech City, TC 12345</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Links Sections */}
          {Object.entries(footerLinks).map(([category, links], index) => (
            <motion.div
              key={category}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <h4 className="text-white font-semibold mb-4 capitalize font-outfit">
                {category}
              </h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-slate-400 hover:text-blue-400 transition-colors text-sm block"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Divider */}
        <div className="h-px bg-gradient-to-r from-transparent via-slate-700 to-transparent mb-8" />

        {/* Bottom Footer */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          {/* Copyright */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-sm text-slate-400"
          >
            <p>
              © {currentYear} <span className="text-blue-400 font-semibold">HypeLens Pvt Ltd</span>. 
              All rights reserved.
            </p>
            <p className="text-xs mt-1 text-slate-500">
              Crafted with ❤️ by professional developers
            </p>
          </motion.div>

          {/* Social Links */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="flex items-center gap-4"
          >
            {socialLinks.map((social, index) => (
              <motion.a
                key={social.label}
                href={social.href}
                whileHover={{ scale: 1.1, y: -2 }}
                whileTap={{ scale: 0.95 }}
                className="w-10 h-10 rounded-full glass flex items-center justify-center text-slate-400 hover:text-blue-400 hover:border-blue-400 transition-all"
                aria-label={social.label}
              >
                <social.icon className="w-5 h-5" />
              </motion.a>
            ))}
          </motion.div>
        </div>

        {/* Tech Stack Badge */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-8 text-center"
        >
          <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full">
            <span className="text-xs text-slate-400">Built with</span>
            <span className="text-xs font-semibold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Next.js • React • TypeScript • Tailwind CSS • Framer Motion
            </span>
          </div>
        </motion.div>
      </div>
    </footer>
  )
}
