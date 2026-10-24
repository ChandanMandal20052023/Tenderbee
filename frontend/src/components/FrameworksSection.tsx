"use client";

import React, { useEffect, useRef } from "react";
import Link from "next/link";
import { gsap } from "@/lib/animations";

export default function FrameworksSection() {
  const containerRef = useRef<HTMLElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && cardsRef.current) {
          gsap.fromTo(
            cardsRef.current.children,
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
      className="bg-[#EEF1FB] py-20 sm:py-28 px-4 sm:px-6 lg:px-8"
      data-purpose="frameworks-benefits"
    >
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
          <div>
            <span className="text-xs font-bold tracking-widest text-brand-purple uppercase">
              GET BID-READY
            </span>
            <h2 className="mt-2 font-serif text-3xl sm:text-5xl text-brand-charcoal font-normal tracking-tight">
              All the tender intelligence you need
            </h2>
          </div>

          {/* Controls Arrow Carousel */}
          <div className="mt-4 md:mt-0 flex items-center space-x-2">
            <button
              aria-label="Previous"
              className="w-10 h-10 rounded-full border border-gray-300 bg-white/80 flex items-center justify-center text-gray-700 hover:bg-white hover:border-brand-purple transition-all cursor-pointer shadow-xs active:scale-95"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M15 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
              </svg>
            </button>
            <button
              aria-label="Next"
              className="w-10 h-10 rounded-full border border-gray-300 bg-white/80 flex items-center justify-center text-gray-700 hover:bg-white hover:border-brand-purple transition-all cursor-pointer shadow-xs active:scale-95"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M9 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
              </svg>
            </button>
          </div>
        </div>

        {/* 3-Card Grid */}
        <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
          {/* Card 1: Discover */}
          <div className="bg-white rounded-3xl p-8 border border-white/80 flex flex-col justify-between min-h-[350px] shadow-[0_10px_30px_-10px_rgba(35,23,85,0.06)] hover:shadow-lg hover:-translate-y-1 transition-all group">
            <div>
              <h3 className="font-serif text-2xl text-brand-charcoal font-semibold">
                Discover Opportunities
              </h3>
              <p className="mt-3 text-sm text-brand-muted leading-relaxed">
                Find tenders aligned with your business profile, registered categories, and geographic target regions.
              </p>
            </div>
            <div className="mt-12 flex justify-start">
              {/* Circular Outline Badge Icon */}
              <div className="w-24 h-24 rounded-full border border-gray-900/80 flex flex-col items-center justify-center text-center p-2 group-hover:scale-105 group-hover:border-brand-purple group-hover:bg-purple-50/50 transition-all">
                <span className="text-xs font-bold uppercase tracking-wider text-gray-800">
                  GeM &amp; CPPP
                </span>
                <span className="text-[10px] text-gray-500 font-medium">Live Sync</span>
              </div>
            </div>
          </div>

          {/* Card 2: Eligibility */}
          <div className="bg-white rounded-3xl p-8 border border-white/80 flex flex-col justify-between min-h-[350px] shadow-[0_10px_30px_-10px_rgba(35,23,85,0.06)] hover:shadow-lg hover:-translate-y-1 transition-all group">
            <div>
              <h3 className="font-serif text-2xl text-brand-charcoal font-semibold">
                Check Eligibility
              </h3>
              <p className="mt-3 text-sm text-brand-muted leading-relaxed">
                Understand mandatory turnover thresholds, EMD exemptions, and prior experience clauses before investing time.
              </p>
            </div>
            <div className="mt-12 flex justify-start">
              <div className="w-24 h-24 rounded-full border border-gray-900/80 flex flex-col items-center justify-center text-center p-2 group-hover:scale-105 group-hover:border-brand-purple group-hover:bg-purple-50/50 transition-all">
                <span className="text-xs font-bold uppercase tracking-wider text-gray-800">
                  Pre-Qual
                </span>
                <span className="text-[10px] text-gray-500 font-medium">Audit Score</span>
              </div>
            </div>
          </div>

          {/* Card 3: Bid-Ready */}
          <div className="bg-white rounded-3xl p-8 border border-white/80 flex flex-col justify-between min-h-[350px] shadow-[0_10px_30px_-10px_rgba(35,23,85,0.06)] hover:shadow-lg hover:-translate-y-1 transition-all group">
            <div>
              <h3 className="font-serif text-2xl text-brand-charcoal font-semibold">
                Stay Bid-Ready
              </h3>
              <p className="mt-3 text-sm text-brand-muted leading-relaxed">
                Track statutory documentation, CA UDIN certs, addenda amendments, and submission checklists effortlessly.
              </p>
            </div>
            <div className="mt-12 flex justify-start">
              <div className="w-24 h-24 rounded-full border border-gray-900/80 flex flex-col items-center justify-center text-center p-2 group-hover:scale-105 group-hover:border-brand-purple group-hover:bg-purple-50/50 transition-all">
                <span className="text-xs font-bold uppercase tracking-wider text-gray-800">
                  100% Ready
                </span>
                <span className="text-[10px] text-gray-500 font-medium">Verification</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action Pill Button */}
        <div className="mt-12">
          <Link
            href="/dashboard"
            className="inline-flex items-center pl-6 pr-2 py-2 text-sm font-semibold text-white bg-brand-purple hover:bg-brand-hover rounded-full transition-all group shadow-sm hover:shadow"
          >
            <span>Explore all categories</span>
            <span className="w-8 h-8 ml-3 rounded-full bg-white/20 group-hover:bg-white/30 flex items-center justify-center transition-colors">
              <svg className="w-4 h-4 text-white stroke-[2.5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
          </Link>
        </div>
      </div>
    </section>
  );
}
