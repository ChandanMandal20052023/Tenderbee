"use client";

import React from "react";

export default function ReadinessGaugeCard() {
  return (
    <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/30 flex flex-col justify-between h-full">
      {/* Card Header */}
      <div className="flex items-start justify-between flex-wrap gap-2">
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
            Readiness Benchmark
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl text-primary mt-1 font-bold">
            Autonomous Envelope Readiness Index
          </h2>
        </div>
        <div className="flex items-center gap-2 bg-surface-container-low px-3 py-1 rounded-full border border-outline-variant/20">
          <span className="w-2 h-2 rounded-full bg-error animate-ping" />
          <span className="text-[10px] text-on-surface font-bold uppercase">
            Submission Lock Engaged
          </span>
        </div>
      </div>

      {/* Scorecard Visual & Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 my-6 items-center">
        {/* Circular / Numeric Gauge Visual (5 cols) */}
        <div className="md:col-span-5 flex items-center gap-4">
          <div className="relative w-36 h-36 flex items-center justify-center shrink-0">
            {/* SVG Radial Gauge */}
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
              <circle
                className="text-surface-container-high"
                cx="60"
                cy="60"
                fill="transparent"
                r="50"
                stroke="currentColor"
                strokeWidth="10"
              />
              {/* 88% stroke dash = 314 * 0.88 = 276.32 => stroke-dashoffset = 37.68 */}
              <circle
                className="text-secondary"
                cx="60"
                cy="60"
                fill="transparent"
                r="50"
                stroke="currentColor"
                strokeDasharray="314"
                strokeDashoffset="37.68"
                strokeLinecap="round"
                strokeWidth="10"
              />
              {/* Threshold Marker line at 95% = 314 * 0.95 = 298.3 */}
              <circle
                className="text-primary-container"
                cx="60"
                cy="60"
                fill="transparent"
                r="50"
                stroke="currentColor"
                strokeDasharray="2 312"
                strokeDashoffset="-298"
                strokeLinecap="butt"
                strokeWidth="12"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="font-serif text-4xl text-primary font-bold leading-none">88</span>
              <span className="text-[10px] font-bold text-on-surface-variant uppercase mt-1">/ 100 PTS</span>
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-xs font-bold text-primary">Conditional Quality</span>
            <p className="text-xs text-on-surface-variant leading-snug">
              Minimum safe threshold for Envelope Lock is <strong className="text-primary font-bold">95 PTS</strong>.
            </p>
            <div className="flex items-center gap-1.5 mt-2">
              <span className="material-symbols-outlined text-base text-secondary">trending_up</span>
              <span className="text-[10px] text-secondary font-bold uppercase tracking-wide">
                +12 PTS Available in Remediation
              </span>
            </div>
          </div>
        </div>

        {/* Score Breakdown Badges & Threshold Bar (7 cols) */}
        <div className="md:col-span-7 flex flex-col gap-2.5 pl-0 md:pl-4">
          <div className="flex items-center justify-between text-on-surface text-xs mb-1">
            <span className="font-medium">Gate Progress: Technical &amp; Statutory Envelope</span>
            <span className="font-bold text-primary">88% (Gap: 7% to Lock)</span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-surface-container-high h-2.5 rounded-full overflow-hidden flex">
            <div className="bg-secondary h-full rounded-l-full" style={{ width: "88%" }} />
            <div className="bg-error-container h-full" style={{ width: "7%" }} />
            <div className="bg-surface-container h-full" style={{ width: "5%" }} />
          </div>

          {/* 3 Status Badges */}
          <div className="grid grid-cols-3 gap-2 mt-2">
            <div className="bg-error-container/60 p-2.5 rounded-xl flex flex-col items-start border border-error/20">
              <div className="flex items-center gap-1 text-on-error-container">
                <span className="material-symbols-outlined text-base">cancel</span>
                <span className="text-xs font-bold">1 Critical</span>
              </div>
              <span className="text-[9px] font-bold text-on-error-container mt-0.5">CSPO / NSIC</span>
            </div>

            <div className="bg-secondary-fixed p-2.5 rounded-xl flex flex-col items-start border border-secondary/20">
              <div className="flex items-center gap-1 text-on-secondary-fixed">
                <span className="material-symbols-outlined text-base">warning</span>
                <span className="text-xs font-bold">1 Warning</span>
              </div>
              <span className="text-[9px] font-bold text-on-secondary-fixed mt-0.5">NIC 81210 Affirmation</span>
            </div>

            <div className="bg-surface-container-low p-2.5 rounded-xl flex flex-col items-start border border-outline-variant/30">
              <div className="flex items-center gap-1 text-secondary">
                <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
                  check_circle
                </span>
                <span className="text-xs font-bold text-on-surface">4 Verified</span>
              </div>
              <span className="text-[9px] font-bold text-on-surface-variant mt-0.5">All Core Layers</span>
            </div>
          </div>
        </div>
      </div>

      {/* Strict Audit Notice */}
      <div className="bg-error-container/40 p-3.5 rounded-xl flex items-center gap-3 text-on-error-container border border-error/20">
        <span className="material-symbols-outlined shrink-0 text-2xl">gavel</span>
        <p className="text-xs leading-snug">
          <strong className="font-bold">Notice:</strong> High score is not permission to submit. 1 mandatory statutory certificate is absent from the staging bundle. Premature sealing will cause automatic tender disqualification at Technical Stage 1.
        </p>
      </div>
    </div>
  );
}
