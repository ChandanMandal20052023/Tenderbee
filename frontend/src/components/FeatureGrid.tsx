"use client";

import React, { useEffect, useRef } from "react";
import { gsap } from "@/lib/animations";

export default function FeatureGrid() {
  const containerRef = useRef<HTMLElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && gridRef.current) {
          gsap.fromTo(
            gridRef.current.children,
            { opacity: 0, y: 24 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: "power2.out" }
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
    <section ref={containerRef} className="py-24 sm:py-32 bg-white px-4 sm:px-6 lg:px-8" data-purpose="core-features">
      <div className="max-w-7xl mx-auto">
        {/* Section Headline */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="font-serif text-4xl sm:text-5xl font-normal text-brand-charcoal tracking-tight">
            It’s all here
          </h2>
          <p className="mt-3 text-base sm:text-lg text-brand-muted leading-relaxed">
            Compliance, qualification, and automated proof. All in the #1 Tender Intelligence Platform.
          </p>
        </div>

        {/* Feature Card Grid with realistic soft UI previews */}
        <div ref={gridRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Feature 1: AI Tender Matching */}
          <div className="bg-[#FAFBFD] rounded-3xl p-6 border border-gray-100/90 flex flex-col justify-between hover:border-brand-purple/30 hover:shadow-lg hover:-translate-y-1 transition-all group">
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6 min-h-[150px] flex flex-col justify-center">
              <div className="flex items-center justify-between bg-gray-50/80 p-2.5 rounded-xl mb-2">
                <span className="text-xs font-semibold text-gray-800">Daily Central Feed</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              </div>
              <div className="bg-indigo-50/80 p-2.5 rounded-xl text-center border border-indigo-100/40">
                <span className="text-xs font-bold text-brand-purple">42 New Tenders Aligned</span>
              </div>
            </div>
            <div>
              <h3 className="font-serif text-xl font-bold text-brand-charcoal">AI-Powered Tender Matching</h3>
              <p className="mt-2 text-xs sm:text-sm text-brand-muted leading-relaxed">
                Continuous monitoring across central and state e-procurement portals matching your capability.
              </p>
            </div>
          </div>

          {/* Feature 2: Pre-Qualification Analysis */}
          <div className="bg-[#FAFBFD] rounded-3xl p-6 border border-gray-100/90 flex flex-col justify-between hover:border-brand-purple/30 hover:shadow-lg hover:-translate-y-1 transition-all group">
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6 min-h-[150px] flex flex-col justify-center">
              <div className="flex items-center justify-between text-xs font-medium text-gray-700 pb-2 border-b border-gray-100">
                <span>Avg Turnover (3 Yrs)</span>
                <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded-full text-[11px]">Pass</span>
              </div>
              <div className="flex items-center justify-between text-xs font-medium text-gray-700 py-2 border-b border-gray-100">
                <span>Similar Work Order</span>
                <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded-full text-[11px]">Pass</span>
              </div>
              <div className="flex items-center justify-between text-xs font-medium text-gray-700 pt-2">
                <span>EMD Exemption</span>
                <span className="text-brand-purple font-bold bg-purple-50 px-2 py-0.5 rounded-full text-[11px]">Eligible</span>
              </div>
            </div>
            <div>
              <h3 className="font-serif text-xl font-bold text-brand-charcoal">Eligibility &amp; Qualification</h3>
              <p className="mt-2 text-xs sm:text-sm text-brand-muted leading-relaxed">
                Instant analysis of turnover, CA UDIN, solvency ratios, and NIC code qualification rules.
              </p>
            </div>
          </div>

          {/* Feature 3: Document Readiness Checklists */}
          <div className="bg-[#FAFBFD] rounded-3xl p-6 border border-gray-100/90 flex flex-col justify-between hover:border-brand-purple/30 hover:shadow-lg hover:-translate-y-1 transition-all group">
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6 min-h-[150px] flex flex-col justify-center space-y-2">
              <div className="flex items-center gap-2 text-xs text-gray-800 bg-emerald-50/80 px-2.5 py-1.5 rounded-lg border border-emerald-100/60">
                <svg className="w-3.5 h-3.5 text-emerald-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path clipRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" fillRule="evenodd" />
                </svg>
                <span className="font-medium">GST 3B Filings</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-800 bg-emerald-50/80 px-2.5 py-1.5 rounded-lg border border-emerald-100/60">
                <svg className="w-3.5 h-3.5 text-emerald-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path clipRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" fillRule="evenodd" />
                </svg>
                <span className="font-medium">Non-Debarment Affidavit</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600 bg-gray-50/80 px-2.5 py-1.5 rounded-lg border border-gray-100">
                <span className="w-3.5 h-3.5 rounded-full border-2 border-gray-400 shrink-0"></span>
                <span className="font-medium">Solvency Certificate</span>
              </div>
            </div>
            <div>
              <h3 className="font-serif text-xl font-bold text-brand-charcoal">Document Checklists</h3>
              <p className="mt-2 text-xs sm:text-sm text-brand-muted leading-relaxed">
                Detect missing certificates, expired notarizations, or unformatted annexures before upload.
              </p>
            </div>
          </div>

          {/* Feature 4: Deadline & Amendment Alerts */}
          <div className="bg-[#FAFBFD] rounded-3xl p-6 border border-gray-100/90 flex flex-col justify-between hover:border-brand-purple/30 hover:shadow-lg hover:-translate-y-1 transition-all group">
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6 min-h-[150px] flex flex-col justify-center">
              <div className="bg-amber-50 border border-amber-200/60 p-3 rounded-xl text-left">
                <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                  <svg className="w-4 h-4 text-amber-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                  </svg>
                  <span>Corrigendum #02</span>
                </div>
                <p className="text-[11px] text-amber-800 mt-1 leading-snug">
                  Bid submission date extended by 7 days. BOQ format revised.
                </p>
              </div>
            </div>
            <div>
              <h3 className="font-serif text-xl font-bold text-brand-charcoal">Deadline &amp; Amendment Alerts</h3>
              <p className="mt-2 text-xs sm:text-sm text-brand-muted leading-relaxed">
                Instant alerts whenever buyers issue Corrigenda, technical revisions, or pre-bid responses.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
