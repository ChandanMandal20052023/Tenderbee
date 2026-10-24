"use client";

import React, { useRef } from "react";
import { useGSAP } from "@gsap/react";
import { gsap } from "@/lib/animations";

export default function VerificationMatrix() {
  const containerRef = useRef<HTMLElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (prefersReduced) return;

      if (gridRef.current) {
        gsap.fromTo(
          gridRef.current.children,
          { opacity: 0, y: 25 },
          {
            opacity: 1,
            y: 0,
            duration: 0.7,
            stagger: 0.08,
            ease: "power2.out",
          }
        );
      }
    },
    { scope: containerRef }
  );

  return (
    <section ref={containerRef} className="flex flex-col gap-4">
      {/* Header Strip */}
      <div className="flex items-end justify-between flex-wrap gap-2">
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-secondary font-bold">
            Deep Architecture
          </span>
          <h2 className="font-serif text-2xl sm:text-3xl text-primary font-bold">
            5-Layer Statutory Verification Matrix
          </h2>
        </div>
        <div className="flex items-center gap-2 text-on-surface-variant text-[11px] font-semibold uppercase tracking-wider">
          <span>Engine Latency: 1.4s</span>
          <span>·</span>
          <span>SHA-256 Validated</span>
        </div>
      </div>

      {/* 5-Column Grid */}
      <div ref={gridRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Layer 01 */}
        <div className="bg-surface-container-lowest rounded-2xl p-5 shadow-sm border border-outline-variant/30 flex flex-col justify-between transition-all hover:shadow-md hover:-translate-y-0.5">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
                Layer 01
              </span>
              <span className="flex items-center gap-1 text-[10px] bg-secondary-fixed text-on-secondary-fixed px-2 py-0.5 rounded-full font-bold">
                <span className="material-symbols-outlined text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>
                  check
                </span>
                PASS
              </span>
            </div>
            <h3 className="font-serif text-lg text-primary mt-1 font-bold">File Integrity &amp; DSC</h3>
            <p className="text-xs text-on-surface-variant leading-snug">
              PDF/A-1b standard conformance. PKCS#7 digital token verified against CCA root.
            </p>
          </div>
          <div className="mt-4 pt-2 bg-surface-container-low p-2.5 rounded-xl flex flex-col gap-1 text-on-surface-variant text-xs border border-outline-variant/20">
            <div className="flex justify-between">
              <span>Scan Quality:</span>
              <span className="font-bold text-on-surface">300 DPI Clear</span>
            </div>
            <div className="flex justify-between">
              <span>DSC Token:</span>
              <span className="font-bold text-on-surface">Class-3 Active</span>
            </div>
          </div>
        </div>

        {/* Layer 02 */}
        <div className="bg-surface-container-lowest rounded-2xl p-5 shadow-sm border border-outline-variant/30 flex flex-col justify-between transition-all hover:shadow-md hover:-translate-y-0.5">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
                Layer 02
              </span>
              <span className="flex items-center gap-1 text-[10px] bg-secondary-fixed text-on-secondary-fixed px-2 py-0.5 rounded-full font-bold">
                <span className="material-symbols-outlined text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>
                  check
                </span>
                PASS
              </span>
            </div>
            <h3 className="font-serif text-lg text-primary mt-1 font-bold">OCR &amp; UDIN Match</h3>
            <p className="text-xs text-on-surface-variant leading-snug">
              Chartered Accountant UDIN authentic. Turnover matches audited balance sheet.
            </p>
          </div>
          <div className="mt-4 pt-2 bg-surface-container-low p-2.5 rounded-xl flex flex-col gap-1 text-on-surface-variant text-xs border border-outline-variant/20">
            <div className="flex justify-between">
              <span>Req. Turnover:</span>
              <span className="text-on-surface font-semibold">₹1.20 Cr</span>
            </div>
            <div className="flex justify-between">
              <span>Found Turnover:</span>
              <span className="font-bold text-secondary">₹1.82 Cr</span>
            </div>
          </div>
        </div>

        {/* Layer 03 */}
        <div className="bg-surface-container-lowest rounded-2xl p-5 shadow-sm border border-outline-variant/30 flex flex-col justify-between transition-all hover:shadow-md hover:-translate-y-0.5">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
                Layer 03
              </span>
              <span className="flex items-center gap-1 text-[10px] bg-secondary-fixed text-on-secondary-fixed px-2 py-0.5 rounded-full font-bold">
                <span className="material-symbols-outlined text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>
                  check
                </span>
                PASS
              </span>
            </div>
            <h3 className="font-serif text-lg text-primary mt-1 font-bold">Entity Consistency</h3>
            <p className="text-xs text-on-surface-variant leading-snug">
              100% legal name alignment across MCA, PAN, GSTIN, and GeM Seller profile.
            </p>
          </div>
          <div className="mt-4 pt-2 bg-surface-container-low p-2.5 rounded-xl flex flex-col gap-1 text-on-surface-variant text-xs border border-outline-variant/20">
            <div className="flex justify-between">
              <span>PAN vs GST:</span>
              <span className="font-bold text-on-surface">Matched</span>
            </div>
            <div className="flex justify-between">
              <span>Corporate ID:</span>
              <span className="font-bold text-on-surface">U74999DL...</span>
            </div>
          </div>
        </div>

        {/* Layer 04 */}
        <div className="bg-surface-container-lowest rounded-2xl p-5 shadow-sm border border-outline-variant/30 flex flex-col justify-between transition-all hover:shadow-md hover:-translate-y-0.5">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
                Layer 04
              </span>
              <span className="flex items-center gap-1 text-[10px] bg-secondary-fixed text-on-secondary-fixed px-2 py-0.5 rounded-full font-bold">
                <span className="material-symbols-outlined text-xs">priority_high</span>
                WARNING
              </span>
            </div>
            <h3 className="font-serif text-lg text-primary mt-1 font-bold">Tender Rule Fit</h3>
            <p className="text-xs text-on-surface-variant leading-snug">
              CPWD Clause 14 requires mechanised cleaning classification under NIC 81210.
            </p>
          </div>
          <div className="mt-4 pt-2 bg-surface-container-low p-2.5 rounded-xl flex flex-col gap-1 text-on-surface-variant text-xs border border-outline-variant/20">
            <div className="flex justify-between">
              <span>Current Code:</span>
              <span className="text-on-surface font-bold">NIC 81210 (Gen)</span>
            </div>
            <div className="flex justify-between text-error font-bold">
              <span>Affirmation:</span>
              <span>Pending Sign</span>
            </div>
          </div>
        </div>

        {/* Layer 05 */}
        <div className="bg-surface-container-lowest rounded-2xl p-5 shadow-sm border border-outline-variant/30 flex flex-col justify-between transition-all hover:shadow-md hover:-translate-y-0.5">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-bold">
                Layer 05
              </span>
              <span className="flex items-center gap-1 text-[10px] bg-error-container text-on-error-container px-2 py-0.5 rounded-full font-bold">
                <span className="material-symbols-outlined text-xs">close</span>
                ACTION REQ
              </span>
            </div>
            <h3 className="font-serif text-lg text-primary mt-1 font-bold">Statutory Regs</h3>
            <p className="text-xs text-on-surface-variant leading-snug">
              Technical competency certificate or CSPO/NSIC enlistment is unattached.
            </p>
          </div>
          <div className="mt-4 pt-2 bg-error-container/40 p-2.5 rounded-xl flex flex-col gap-1 text-on-error-container text-xs border border-error/20">
            <div className="flex justify-between">
              <span>Missing Doc:</span>
              <span className="font-bold">CSPO / NSIC</span>
            </div>
            <div className="flex justify-between">
              <span>Disqualification:</span>
              <span className="font-bold text-error">Stage 1 Risk</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
