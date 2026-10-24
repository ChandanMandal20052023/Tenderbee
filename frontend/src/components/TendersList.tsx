"use client";

import React from "react";
import Link from "next/link";

export default function TendersList() {
  return (
    <div className="flex flex-col gap-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[10px] text-on-surface-variant uppercase tracking-widest block font-semibold">
            Procurement
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-primary">
            Active Tenders
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 rounded-full neu-button text-on-surface text-xs font-semibold flex items-center gap-1.5 cursor-pointer">
            <span className="material-symbols-outlined text-base">filter_list</span>
            <span>Filter (3)</span>
          </button>
        </div>
      </div>

      {/* Tender Card 1: CPWD Integrated Facility Management */}
      <div className="bg-surface-container-lowest neu-flat rounded-2xl p-6 flex flex-col gap-4 hover:-translate-y-0.5 transition-transform">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl neu-flat-sm bg-primary-container text-on-primary flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">corporate_fare</span>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] px-2 py-0.5 rounded-full neu-pressed-sm text-on-surface-variant font-mono font-medium">
                  CPWD/NZ/2024/718
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full neu-flat-sm bg-secondary-fixed text-on-secondary-fixed font-bold">
                  GeM Custom
                </span>
                <span className="text-[10px] text-on-surface-variant flex items-center gap-1 font-medium">
                  <span className="material-symbols-outlined text-sm">timer</span> 3d 14h left
                </span>
              </div>
              <h3 className="font-serif text-lg sm:text-xl text-primary mt-1 font-bold">
                Integrated Facility Management &amp; Mechanized Operations
              </h3>
              <p className="text-xs text-on-surface-variant">
                Central Public Works Department • Shastri Bhawan, New Delhi
              </p>
            </div>
          </div>
          <div className="flex flex-col md:items-end shrink-0">
            <span className="font-serif text-2xl font-bold text-primary">₹3.90 Cr</span>
            <span className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">
              Value
            </span>
          </div>
        </div>

        {/* Compliance Ribbon - Neumorphic Well */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-xl neu-pressed">
          <div className="flex flex-col">
            <span className="text-[10px] text-on-surface-variant uppercase font-semibold">
              Readiness
            </span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="font-serif text-lg text-secondary font-bold">94%</span>
              <span className="text-xs text-on-surface-variant font-medium">Optimal</span>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-on-surface-variant uppercase font-semibold">
              EMD Status
            </span>
            <span className="text-xs font-semibold text-on-surface mt-0.5 flex items-center gap-1">
              <span className="material-symbols-outlined text-secondary text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
                check_circle
              </span>
              MSE Exemption Claimed
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-on-surface-variant uppercase font-semibold">
              Corrigenda
            </span>
            <span className="text-xs font-medium text-on-surface mt-0.5 flex items-center gap-1">
              <span className="material-symbols-outlined text-on-surface-variant text-base">sync</span>
              Addendum #2 Synced
            </span>
          </div>
        </div>

        {/* Action Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-secondary" />
            <span className="text-xs text-on-surface-variant">
              Verdict: <strong className="text-on-surface">Substantially Responsive</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button className="px-3.5 py-1.5 rounded-full neu-button text-on-surface text-xs font-semibold cursor-pointer">
              BOQ
            </button>
            <Link
              href="/audit"
              className="px-4 py-1.5 rounded-full neu-button-primary text-xs font-semibold flex items-center gap-1"
            >
              <span>Audit Verdict</span>
              <span className="material-symbols-outlined text-base">chevron_right</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Tender Card 2: Indian Railways Housekeeping */}
      <div className="bg-surface-container-lowest neu-flat rounded-2xl p-6 flex flex-col gap-4 hover:-translate-y-0.5 transition-transform">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl neu-flat-sm bg-tertiary-container text-tertiary-fixed flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">train</span>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] px-2 py-0.5 rounded-full neu-pressed-sm text-on-surface-variant font-mono font-medium">
                  IREPS/NR/HK-2024
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full neu-flat-sm bg-error-container text-on-error-container font-bold">
                  Action Required
                </span>
                <span className="text-[10px] text-on-surface-variant flex items-center gap-1 font-medium">
                  <span className="material-symbols-outlined text-sm">timer</span> 18h left
                </span>
              </div>
              <h3 className="font-serif text-lg sm:text-xl text-primary mt-1 font-bold">
                Mechanized Housekeeping Services (OBHS)
              </h3>
              <p className="text-xs text-on-surface-variant">
                Northern Railway • New Delhi Division
              </p>
            </div>
          </div>
          <div className="flex flex-col md:items-end shrink-0">
            <span className="font-serif text-2xl font-bold text-primary">₹1.45 Cr</span>
            <span className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">
              Value
            </span>
          </div>
        </div>

        {/* Warning Callout Box - Neumorphic Well */}
        <div className="p-3.5 rounded-xl neu-pressed flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <span className="material-symbols-outlined text-error text-xl shrink-0 mt-0.5">warning</span>
            <div className="flex flex-col">
              <span className="text-xs font-bold text-on-surface">Missing CSPO Attestation</span>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Clause 4.3(b) requires ISO 45001 scope endorsement for railway pantry services.
              </p>
            </div>
          </div>
          <Link
            href="/audit"
            className="px-3.5 py-1.5 rounded-full neu-button text-primary text-xs font-semibold shrink-0 self-start sm:self-auto text-center"
          >
            Upload Doc
          </Link>
        </div>

        {/* Action Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-error" />
            <span className="text-xs text-on-surface-variant">
              Readiness: <strong className="text-error">72% (Risk of Rejection)</strong>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/audit"
              className="px-3.5 py-1.5 rounded-full neu-button text-on-surface text-xs font-semibold"
            >
              Audit Details
            </Link>
            <Link
              href="/audit"
              className="px-4 py-1.5 rounded-full neu-button-primary text-xs font-semibold flex items-center gap-1"
            >
              <span>Resolve</span>
              <span className="material-symbols-outlined text-base">arrow_forward</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Tender Card 3: AIIMS Sanitization */}
      <div className="bg-surface-container-lowest neu-flat rounded-2xl p-6 flex flex-col gap-4 hover:-translate-y-0.5 transition-transform">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl neu-flat-sm bg-secondary-fixed text-on-secondary-fixed flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">local_hospital</span>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] px-2 py-0.5 rounded-full neu-pressed-sm text-on-surface-variant font-mono font-medium">
                  AIIMS-DELHI/2024/SAN-41
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full neu-flat-sm text-on-surface-variant font-bold">
                  Technical Ready
                </span>
                <span className="text-[10px] text-on-surface-variant flex items-center gap-1 font-medium">
                  <span className="material-symbols-outlined text-sm">timer</span> 6d left
                </span>
              </div>
              <h3 className="font-serif text-lg sm:text-xl text-primary mt-1 font-bold">
                Hospital Bio-Sanitization &amp; Environmental Sterilization
              </h3>
              <p className="text-xs text-on-surface-variant">
                AIIMS New Delhi • Main Hospital Wing
              </p>
            </div>
          </div>
          <div className="flex flex-col md:items-end shrink-0">
            <span className="font-serif text-2xl font-bold text-primary">₹85.0 L</span>
            <span className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">
              Value
            </span>
          </div>
        </div>

        {/* Compliance Ribbon - Neumorphic Well */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 rounded-xl neu-pressed">
          <div className="flex flex-col">
            <span className="text-[10px] text-on-surface-variant uppercase font-semibold">Audit</span>
            <span className="text-xs font-bold text-secondary mt-0.5 flex items-center gap-1">
              <span className="material-symbols-outlined text-secondary text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
                verified
              </span>
              100% Verified
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-on-surface-variant uppercase font-semibold">Experience</span>
            <span className="text-xs font-semibold text-on-surface mt-0.5">Safdarjung 2022-23</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-on-surface-variant uppercase font-semibold">Clarifications</span>
            <span className="text-xs font-semibold text-on-surface mt-0.5">3 Logged</span>
          </div>
        </div>

        {/* Action Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-secondary" />
            <span className="text-xs text-on-surface-variant">
              Bid pack ready for DSC token sign-off
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button className="px-3.5 py-1.5 rounded-full neu-button text-on-surface text-xs font-semibold cursor-pointer">
              Review
            </button>
            <button className="px-4 py-1.5 rounded-full neu-button-primary text-xs font-semibold flex items-center gap-1 cursor-pointer">
              <span>Sign (Class-3 DSC)</span>
              <span className="material-symbols-outlined text-base">enhanced_encryption</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
