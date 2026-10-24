"use client";

import React, { useRef } from "react";
import Link from "next/link";
import { useGSAP } from "@gsap/react";
import { gsap } from "@/lib/animations";

export default function MetricCards() {
  const containerRef = useRef<HTMLElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (prefersReduced) return;

      if (gridRef.current) {
        gsap.from(gridRef.current.children, {
          opacity: 0,
          y: 20,
          duration: 0.7,
          stagger: 0.1,
          ease: "power2.out",
        });
      }
    },
    { scope: containerRef }
  );

  return (
    <section ref={containerRef} className="px-4 sm:px-8 xl:px-12 pb-8">
      <div ref={gridRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 1. Overall Bid Readiness Index */}
        <div className="relative bg-surface-container-lowest rounded-2xl p-6 shadow-[0_12px_32px_-4px_rgba(59,0,102,0.05)] border border-outline-variant/30 flex flex-col justify-between min-h-[250px] overflow-hidden group">
          <div className="absolute -top-12 -right-12 w-32 h-32 bg-secondary-fixed/40 rounded-full blur-2xl group-hover:scale-125 transition-transform" />
          <div className="flex items-start justify-between relative z-10">
            <div>
              <span className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">
                Autonomous Health
              </span>
              <span className="font-serif text-xl font-bold text-primary">Readiness Index</span>
            </div>
            <span className="p-2 rounded-full bg-secondary-fixed text-on-secondary-fixed flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">fact_check</span>
            </span>
          </div>

          <div className="flex items-center gap-4 my-3 relative z-10">
            {/* Circular Progress Gauge */}
            <div className="relative w-20 h-20 shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-surface-container"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3.5"
                />
                <path
                  className="text-secondary stroke-current"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  strokeDasharray="88, 100"
                  strokeLinecap="round"
                  strokeWidth="3.5"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className="font-serif text-xl font-bold text-primary leading-none">88</span>
                <span className="text-[10px] text-on-surface-variant font-semibold leading-none mt-0.5">/100</span>
              </div>
            </div>

            <div className="flex flex-col">
              <div className="flex items-center gap-1 text-secondary font-semibold text-xs">
                <span className="material-symbols-outlined text-sm">trending_up</span>
                <span>+16 pts this week</span>
              </div>
              <p className="text-xs text-on-surface-variant mt-1 leading-snug">
                Top percentile among Facility Class 1 MSE suppliers.
              </p>
            </div>
          </div>

          <div className="pt-2 border-t border-outline-variant/20 relative z-10 flex items-center justify-between text-on-surface-variant">
            <span className="text-[10px] uppercase font-semibold">Target: 95+ (Guaranteed Pass)</span>
            <span className="text-[10px] font-bold text-secondary">8 pts to peak</span>
          </div>
        </div>

        {/* 2. Active Pipeline Value */}
        <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-[0_12px_32px_-4px_rgba(59,0,102,0.05)] border border-outline-variant/30 flex flex-col justify-between min-h-[250px]">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">
                Central Radar
              </span>
              <span className="font-serif text-xl font-bold text-primary">Tenders Tracked</span>
            </div>
            <span className="p-2 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">gavel</span>
            </span>
          </div>

          <div className="my-3">
            <div className="flex items-baseline gap-2">
              <span className="font-serif text-4xl text-primary font-bold leading-none">14</span>
              <span className="text-sm font-medium text-on-surface-variant">Bids Live</span>
            </div>
            <div className="mt-2 flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed text-[11px] font-bold">
                ₹18.4 Cr Pipeline
              </span>
              <span className="text-xs text-on-surface-variant">4 bids closing &lt;48h</span>
            </div>
          </div>

          {/* Inline Visual Spark-Bars */}
          <div className="flex items-end gap-1.5 h-6 w-full pt-1">
            <div className="h-3 w-1/6 bg-secondary-fixed rounded-t-sm" title="CPWD" />
            <div className="h-5 w-1/6 bg-secondary rounded-t-sm" title="Railways" />
            <div className="h-4 w-1/6 bg-secondary-fixed rounded-t-sm" title="AIIMS" />
            <div className="h-6 w-1/6 bg-primary rounded-t-sm" title="MES" />
            <div className="h-2 w-1/6 bg-surface-container-highest rounded-t-sm" title="ONGC" />
            <div className="h-4 w-1/6 bg-secondary rounded-t-sm" title="DRDO" />
          </div>
        </div>

        {/* 3. Compliance Health */}
        <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-[0_12px_32px_-4px_rgba(59,0,102,0.05)] border border-outline-variant/30 flex flex-col justify-between min-h-[250px]">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">
                Clause Integrity
              </span>
              <span className="font-serif text-xl font-bold text-primary">Compliance Health</span>
            </div>
            <span className="p-2 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">rule</span>
            </span>
          </div>

          <div className="my-3">
            <div className="flex items-baseline gap-2">
              <span className="font-serif text-4xl text-primary font-bold leading-none">99.2%</span>
              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-surface-container text-on-surface-variant">
                Audited
              </span>
            </div>
            <div className="mt-2 flex items-center gap-1.5 text-on-surface-variant text-xs">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <span>27/28 clauses verified clean</span>
            </div>
          </div>

          <div className="flex items-center gap-2 p-2.5 rounded-xl bg-surface-container-low text-on-surface border border-outline-variant/20">
            <span className="material-symbols-outlined text-base text-error">priority_high</span>
            <span className="text-xs truncate font-medium">1 attention item: CSPO exemption doc</span>
          </div>
        </div>

        {/* 4. Corrigendum Alerts */}
        <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-[0_12px_32px_-4px_rgba(59,0,102,0.05)] border border-outline-variant/30 flex flex-col justify-between min-h-[250px]">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] text-on-surface-variant uppercase tracking-wider block font-semibold">
                GeM &amp; CPPP Feed
              </span>
              <span className="font-serif text-xl font-bold text-primary">Corrigenda</span>
            </div>
            <div className="relative">
              <span className="p-2 rounded-full bg-secondary-fixed text-on-secondary-fixed flex items-center justify-center">
                <span className="material-symbols-outlined text-xl">radar</span>
              </span>
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-secondary rounded-full animate-ping" />
            </div>
          </div>

          <div className="my-3">
            <div className="flex items-baseline gap-2">
              <span className="font-serif text-4xl text-primary font-bold leading-none">3</span>
              <span className="text-sm font-medium text-on-surface-variant">New (24h)</span>
            </div>
            <p className="text-xs text-on-surface-variant mt-2 leading-relaxed">
              Addenda parsed autonomously. BOQ specs shifted for AIIMS tender.
            </p>
          </div>

          <Link
            href="/audit"
            className="flex items-center justify-between text-secondary text-xs font-semibold hover:underline pt-2 border-t border-outline-variant/20"
          >
            <span>Inspect Addendum Diff</span>
            <span className="material-symbols-outlined text-base">north_east</span>
          </Link>
        </div>
      </div>
    </section>
  );
}
