"use client";

import React, { useEffect, useRef } from "react";
import Link from "next/link";
import { gsap } from "@/lib/animations";

export default function BuiltForYouSection() {
  const containerRef = useRef<HTMLElement>(null);
  const stepsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && stepsRef.current) {
          gsap.fromTo(
            stepsRef.current.children,
            { opacity: 0, y: 24 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: "power2.out" }
          );
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={containerRef}
      className="bg-brand-eggplant text-white py-24 sm:py-32 px-4 sm:px-6 lg:px-8"
      data-purpose="how-it-works"
    >
      <div className="max-w-7xl mx-auto">
        {/* Section Title */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="font-serif text-4xl sm:text-5xl font-normal text-white tracking-tight">
            Built for you
          </h2>
          <p className="mt-3 text-base sm:text-lg text-purple-200/80 leading-relaxed">
            Whether you&apos;re managing multi-crore EPC tenders or just bidding on your first government project.
          </p>
        </div>

        {/* 3-Column Stepper Cards */}
        <div ref={stepsRef} className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Step 1 Card */}
          <div className="flex flex-col group">
            <div className="bg-[#D1D6F7] rounded-3xl p-6 sm:p-8 h-72 flex items-center justify-center relative overflow-hidden transition-all duration-300 group-hover:shadow-[0_20px_40px_-15px_rgba(209,214,247,0.3)]">
              {/* Illustrated Blueprint Card Frame */}
              <div className="w-48 h-48 bg-white/50 backdrop-blur-xs rounded-2xl flex flex-col items-center justify-center p-4 border border-white/70 shadow-sm group-hover:scale-105 transition-transform duration-300">
                <div className="w-12 h-12 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-purple mb-2 shadow-xs">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                  </svg>
                </div>
                <span className="text-xs font-bold text-gray-900">MSME / Udyam Sync</span>
                <span className="text-[11px] text-gray-600 mt-1 font-medium">Instant GSTIN Parse</span>
              </div>
            </div>
            <div className="mt-6 flex flex-col">
              <h3 className="font-serif text-2xl font-medium text-white">Step 1: Create Your Profile</h3>
              <p className="mt-2 text-sm text-purple-200/80 leading-relaxed">
                Enter your Udyam registration, GSTIN, and past completions to establish automated qualification baselines.
              </p>
              <Link
                href="/dashboard"
                className="mt-4 inline-flex items-center text-sm font-semibold text-brand-periwinkle hover:text-white group/link transition-colors self-start"
              >
                <span>Learn more</span>
                <svg className="w-4 h-4 ml-1 transform group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M14 5l7 7m0 0l-7 7m7-7H3" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
              </Link>
            </div>
          </div>

          {/* Step 2 Card */}
          <div className="flex flex-col group">
            <div className="bg-[#D1D6F7] rounded-3xl p-6 sm:p-8 h-72 flex items-center justify-center relative overflow-hidden transition-all duration-300 group-hover:shadow-[0_20px_40px_-15px_rgba(209,214,247,0.3)]">
              <div className="w-48 h-48 bg-white/50 backdrop-blur-xs rounded-2xl flex flex-col items-center justify-center p-4 border border-white/70 shadow-sm group-hover:scale-105 transition-transform duration-300">
                <div className="w-12 h-12 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-purple mb-2 shadow-xs">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                  </svg>
                </div>
                <span className="text-xs font-bold text-gray-900">AI Clause Scraper</span>
                <span className="text-[11px] text-gray-600 mt-1 font-medium">EMD &amp; Turnover Match</span>
              </div>
            </div>
            <div className="mt-6 flex flex-col">
              <h3 className="font-serif text-2xl font-medium text-white">Step 2: Discover &amp; Analyze</h3>
              <p className="mt-2 text-sm text-purple-200/80 leading-relaxed">
                Live indexation across central and state e-procurement portals with automated clause extraction and scoring.
              </p>
              <Link
                href="/dashboard"
                className="mt-4 inline-flex items-center text-sm font-semibold text-brand-periwinkle hover:text-white group/link transition-colors self-start"
              >
                <span>Learn more</span>
                <svg className="w-4 h-4 ml-1 transform group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M14 5l7 7m0 0l-7 7m7-7H3" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
              </Link>
            </div>
          </div>

          {/* Step 3 Card */}
          <div className="flex flex-col group">
            <div className="bg-[#D1D6F7] rounded-3xl p-6 sm:p-8 h-72 flex items-center justify-center relative overflow-hidden transition-all duration-300 group-hover:shadow-[0_20px_40px_-15px_rgba(209,214,247,0.3)]">
              <div className="w-48 h-48 bg-white/50 backdrop-blur-xs rounded-2xl flex flex-col items-center justify-center p-4 border border-white/70 shadow-sm group-hover:scale-105 transition-transform duration-300">
                <div className="w-12 h-12 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-purple mb-2 shadow-xs">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                  </svg>
                </div>
                <span className="text-xs font-bold text-gray-900">Bid Pack Ready</span>
                <span className="text-[11px] text-gray-600 mt-1 font-medium">Zero Rejection Risks</span>
              </div>
            </div>
            <div className="mt-6 flex flex-col">
              <h3 className="font-serif text-2xl font-medium text-white">Step 3: Prepare &amp; Submit</h3>
              <p className="mt-2 text-sm text-purple-200/80 leading-relaxed">
                Generate grounded compliance sheets and get real-time Corrigendum alerts straight through to submission.
              </p>
              <Link
                href="/audit"
                className="mt-4 inline-flex items-center text-sm font-semibold text-brand-periwinkle hover:text-white group/link transition-colors self-start"
              >
                <span>Learn more</span>
                <svg className="w-4 h-4 ml-1 transform group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M14 5l7 7m0 0l-7 7m7-7H3" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
