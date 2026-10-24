"use client";

import React, { useState } from "react";
import Link from "next/link";

export default function ExecutiveBanner() {
  const [syncing, setSyncing] = useState(false);

  const handleSync = () => {
    setSyncing(true);
    setTimeout(() => {
      setSyncing(false);
    }, 1200);
  };

  return (
    <section className="px-4 sm:px-8 xl:px-12 pt-8 pb-6">
      <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-6">
        <div className="flex flex-col max-w-3xl">
          {/* Metadata Tags */}
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed text-xs uppercase tracking-wider font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary" />
              Class 1 Local Supplier (MSE)
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container text-on-surface-variant text-xs tracking-wide">
              GeM Seller ID: <strong className="font-semibold text-on-surface">GEM/2024/FAC/89410</strong>
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-high text-on-surface-variant text-xs font-mono">
              UDYAM-MH-02-0049182
            </span>
          </div>

          {/* Heading */}
          <h1 className="font-serif text-3xl sm:text-5xl text-primary tracking-tight font-normal">
            Welcome back, <span className="italic font-normal">ABC Facility Services</span>
          </h1>

          {/* Subhead Lead */}
          <p className="text-base sm:text-lg text-on-surface-variant mt-2 leading-relaxed">
            Government e-Marketplace (GeM) and Central CPPP synchronisation is fully operational. 1 critical compliance remediator requires sign-off before 17:00 IST.
          </p>
        </div>

        {/* Quick Action Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleSync}
            className="group flex items-center gap-2.5 pl-4 pr-3 py-2.5 rounded-full bg-surface-container-lowest text-on-surface shadow-[0_12px_32px_-4px_rgba(59,0,102,0.06)] hover:bg-surface-container-low border border-outline-variant/30 transition-all cursor-pointer"
            id="sync-portal-btn"
            type="button"
          >
            <span className={`material-symbols-outlined text-secondary text-xl transition-transform ${syncing ? "animate-spin" : "group-hover:rotate-180"}`}>
              sync
            </span>
            <span className="text-xs sm:text-sm font-semibold">
              {syncing ? "Synchronizing..." : "Sync GeM & CPPP"}
            </span>
            <span className="w-6 h-6 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant text-[11px] font-mono">
              ⌘S
            </span>
          </button>

          <Link
            href="/audit"
            className="group flex items-center gap-3 pl-5 pr-2 py-2 rounded-full bg-primary-container text-on-primary shadow-[0_12px_32px_-4px_rgba(59,0,102,0.2)] hover:bg-primary transition-all cursor-pointer"
          >
            <span className="text-xs sm:text-sm font-semibold tracking-wide">Upload Document for Audit</span>
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-on-secondary shadow-sm transition-transform group-hover:translate-x-0.5">
              <span className="material-symbols-outlined text-lg">arrow_forward</span>
            </div>
          </Link>
        </div>
      </div>
    </section>
  );
}
