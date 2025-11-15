'use client';

import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import CursorFollower from '@/components/layout/CursorFollower';
import HeroSection from '@/components/home/HeroSection';
import HowToUse from '@/components/home/HowToUse';
import FeaturesSection from '@/components/home/FeaturesSection';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950">
      <CursorFollower />
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
