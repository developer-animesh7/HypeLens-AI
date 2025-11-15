'use client'

import { useEffect, useState } from 'react'
import { FiSearch } from 'react-icons/fi'

export default function CursorFollower() {
  const [isVisible, setIsVisible] = useState(false)
  const [isHovering, setIsHovering] = useState(false)
  const [position, setPosition] = useState({ x: -100, y: -100 })

  useEffect(() => {
    const moveCursor = (e: MouseEvent) => {
      // Direct position update - no spring physics for instant response
      setPosition({ x: e.clientX - 30, y: e.clientY - 30 })
      setIsVisible(true)
      
      const target = e.target as HTMLElement
      const isClickable = target.tagName === 'A' || 
                         target.tagName === 'BUTTON' || 
                         target.closest('a') || 
                         target.closest('button') ||
                         target.closest('input')
      setIsHovering(!!isClickable)
    }

    const hideCursor = () => setIsVisible(false)

    window.addEventListener('mousemove', moveCursor)
    window.addEventListener('mouseleave', hideCursor)

    return () => {
      window.removeEventListener('mousemove', moveCursor)
      window.removeEventListener('mouseleave', hideCursor)
    }
  }, [])

  return (
    <>
      {/* Main Lens Cursor */}
      <div
        id="hero-cursor-glow"
        className="fixed top-0 left-0 w-16 h-16 pointer-events-none z-[9999] hidden lg:block transition-opacity duration-200"
        style={{
          transform: `translate(${position.x}px, ${position.y}px)`,
          opacity: isVisible ? 1 : 0,
        }}
      >
        {/* Outer Glowing Ring */}
        <div
          className="absolute inset-0 rounded-full border-2 transition-all duration-300"
          style={{
            borderColor: 'rgba(59, 130, 246, 0.6)',
            boxShadow: '0 0 20px rgba(59, 130, 246, 0.4), inset 0 0 20px rgba(59, 130, 246, 0.2)',
            transform: isHovering ? 'scale(1.3)' : 'scale(1)',
          }}
        />
        
        {/* Lens Background */}
        <div 
          className="absolute inset-4 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.1), transparent)',
          }}
        />
        
        {/* Search Icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className="transition-transform duration-200"
            style={{
              transform: isHovering ? 'scale(1.3) rotate(15deg)' : 'scale(1) rotate(0deg)',
            }}
          >
            <FiSearch className="w-6 h-6 text-blue-400 drop-shadow-[0_0_8px_rgba(59,130,246,0.8)]" />
          </div>
        </div>

        {/* Inner Dot */}
        <div
          className="absolute top-1/2 left-1/2 w-1.5 h-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-400 transition-all duration-200"
          style={{
            transform: `translate(-50%, -50%) scale(${isHovering ? 2 : 1})`,
            boxShadow: isHovering ? '0 0 12px rgba(59, 130, 246, 1)' : '0 0 6px rgba(59, 130, 246, 0.8)',
          }}
        />
      </div>
    </>
  )
}
