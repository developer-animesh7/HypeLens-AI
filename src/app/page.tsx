'use client';

import { useEffect } from 'react';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import HeroSection from '@/components/home/HeroSection';
import HowToUse from '@/components/home/HowToUse';
import FeaturesSection from '@/components/home/FeaturesSection';

export default function Home() {
  useEffect(() => {
    // Prevent auto-scroll on page load
    const scrollY = window.scrollY
    window.scrollTo(0, scrollY)
  }, [])

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      <main>
        <HeroSection />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <HowToUse />
        </div>
        <FeaturesSection />
      </main>
      <Footer />
    </div>
  );
}
