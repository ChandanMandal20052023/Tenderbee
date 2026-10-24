"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useGSAP } from "@gsap/react";
import { gsap } from "@/lib/animations";

export default function HeroSection() {
  const router = useRouter();
  const containerRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);
  const subheadRef = useRef<HTMLParagraphElement>(null);
  const formRef = useRef<HTMLDivElement>(null);
  const mockupRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (prefersReduced) return;

      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
      tl.fromTo(
        headlineRef.current,
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.9 }
      )
        .fromTo(
          subheadRef.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.7 },
          "-=0.5"
        )
        .fromTo(
          formRef.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.7 },
          "-=0.4"
        )
        .fromTo(
          mockupRef.current,
          { opacity: 0, y: 40 },
          { opacity: 1, y: 0, duration: 0.9 },
          "-=0.5"
        );
    },
    { scope: containerRef }
  );

  return (
    <section
      ref={containerRef}
      className="bg-wave-pattern pt-16 sm:pt-24 pb-20 sm:pb-32 px-4 sm:px-6 lg:px-8 border-b border-indigo-100 overflow-hidden"
      data-purpose="hero-section"
    >
      <div className="max-w-4xl mx-auto text-center">
        {/* Display Headline */}
        <h1
          ref={headlineRef}
          className="font-serif editorial-headline text-4xl sm:text-6xl md:text-[68px] leading-[1.08] text-brand-charcoal font-normal tracking-tight"
        >
          Find the Right Tenders Bid with<br className="hidden sm:inline" />
          Confidence
        </h1>

        {/* Supporting Paragraph */}
        <p
          ref={subheadRef}
          className="mt-6 text-base sm:text-lg md:text-xl text-brand-charcoal/80 max-w-2xl mx-auto leading-relaxed"
        >
          Discover relevant opportunities, understand eligibility, and stay prepared with intelligent tender insights.
        </p>

        {/* Pill Action Form Input - Neumorphic Inset & Raised Button */}
        <div ref={formRef} className="mt-8 max-w-xl mx-auto">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              router.push("/dashboard");
            }}
            className="neu-flat p-2 sm:p-2.5 rounded-full flex items-center justify-between gap-2"
          >
            <input
              className="w-full neu-pressed-sm rounded-full py-2.5 pl-5 pr-3 text-sm sm:text-base text-brand-charcoal placeholder-gray-400 outline-none"
              placeholder="Enter your work email or tender category..."
              required
              type="text"
            />
            <button
              className="flex-shrink-0 inline-flex items-center pl-5 pr-2 py-2 text-xs sm:text-sm font-semibold text-white neu-button-primary rounded-full group cursor-pointer"
              type="submit"
            >
              <span>Explore Tenders</span>
              <span className="w-7 h-7 ml-2 rounded-full bg-white/20 group-hover:bg-white/30 flex items-center justify-center transition-colors">
                <svg className="w-3.5 h-3.5 text-white stroke-[2.5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </button>
          </form>
        </div>

        {/* Hero Dashboard Visual Mockup */}
        <div ref={mockupRef} className="mt-12 sm:mt-16 max-w-3xl mx-auto">
          <div className="neu-flat bg-gradient-to-br from-surface-container-low to-surface-container p-3 sm:p-5 rounded-3xl border border-white/80">
            {/* Top Window Controls */}
            <div className="flex items-center space-x-2 mb-4 px-2">
              <span className="w-3 h-3 rounded-full neu-pressed-sm bg-rose-400/80"></span>
              <span className="w-3 h-3 rounded-full neu-pressed-sm bg-amber-400/80"></span>
              <span className="w-3 h-3 rounded-full neu-pressed-sm bg-emerald-400/80"></span>
            </div>

            {/* Tender Mockup Center Card Stack */}
            <div className="neu-pressed rounded-2xl p-6 sm:p-10 flex flex-col items-center justify-center min-h-[260px] sm:min-h-[310px] relative">
              {/* Source Integration Badges */}
              <div className="flex items-center justify-center gap-2 mb-4 flex-wrap">
                <div className="neu-flat-sm rounded-xl px-3 py-1.5 text-xs font-semibold flex items-center gap-2 text-gray-700 bg-surface-container-lowest">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span>GeM Portal</span>
                </div>
                <div className="neu-flat-sm rounded-xl px-3 py-1.5 text-xs font-semibold flex items-center gap-2 text-gray-700 bg-surface-container-lowest">
                  <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                  <span>CPPP National</span>
                </div>
                <div className="neu-flat-sm rounded-xl px-3 py-1.5 text-xs font-semibold flex items-center gap-2 text-gray-700 bg-surface-container-lowest">
                  <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                  <span>State Feeds</span>
                </div>
              </div>

              {/* Foreground Live Tender Card Indicator */}
              <Link
                href="/audit"
                className="w-full max-w-md neu-flat rounded-2xl p-4 transform hover:-translate-y-1 transition-transform text-left cursor-pointer group block"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl neu-flat-sm bg-purple-50 flex items-center justify-center text-brand-purple group-hover:bg-brand-purple group-hover:text-white transition-colors">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="text-xs sm:text-sm font-bold text-gray-900 leading-tight">CPWD Comprehensive Facility Mgmt</h4>
                      <p className="text-[11px] text-gray-500">Ref: GEM/2025/B/91280 • ₹1.84 Cr</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold neu-flat-sm bg-emerald-100 text-emerald-800">
                    94% Match
                  </span>
                </div>

                {/* Quick Progress & Checklist Line */}
                <div className="mt-3.5 pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-600">
                  <span className="flex items-center gap-1.5">
                    <svg className="w-3.5 h-3.5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                      <path clipRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" fillRule="evenodd" />
                    </svg>
                    Eligibility criteria qualified
                  </span>
                  <span className="font-medium text-amber-600 neu-pressed-sm px-2 py-0.5 rounded-md">3 days remaining</span>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
