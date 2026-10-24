"use client";

import React, { useState } from "react";

export default function AuditHeaderStrip() {
  const [selectedBid, setSelectedBid] = useState("gem-992140");

  return (
    <section className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/30 flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative overflow-hidden">
      <div className="flex flex-col gap-2 max-w-2xl">
        {/* Eyebrow Chips */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[10px] uppercase tracking-wider text-secondary font-bold bg-secondary-fixed px-2.5 py-0.5 rounded-full">
            Autonomous Bid Audit
          </span>
          <span className="text-on-surface-variant text-xs">·</span>
          <span className="text-[10px] font-semibold text-on-surface-variant tracking-wider uppercase">
            Portal: GeM v4.2 Enterprise
          </span>
        </div>

        {/* Tender Picker Dropdown */}
        <div className="flex items-center gap-2 mt-1">
          <label className="sr-only" htmlFor="tender-picker">
            Select Bid Subject
          </label>
          <div className="relative inline-flex items-center w-full sm:w-auto">
            <select
              id="tender-picker"
              value={selectedBid}
              onChange={(e) => setSelectedBid(e.target.value)}
              className="appearance-none bg-surface-container-low text-on-surface font-serif text-lg sm:text-xl font-bold pl-4 pr-10 py-2 rounded-xl cursor-pointer focus:outline-none focus:bg-surface-container focus:ring-2 focus:ring-primary/20 border border-outline-variant/30 transition-all w-full sm:w-auto"
            >
              <option value="gem-992140">CPWD Integrated Facility Management · GEM/2025/B/992140</option>
              <option value="cppp-883102">MES Command Hospital HVAC Retrofit · GEM/2025/B/883102</option>
              <option value="eproc-771900">NHAI Highway Intelligent Toll Infrastructure · CPPP/2025/NHAI/04</option>
            </select>
            <span className="material-symbols-outlined absolute right-3 pointer-events-none text-on-surface-variant text-xl">
              expand_more
            </span>
          </div>
        </div>

        {/* Company & Authority Line */}
        <div className="flex items-center gap-4 flex-wrap pt-1 text-on-surface-variant text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-base text-primary">domain</span>
            <span>ABC Facility Services Pvt Ltd</span>
          </div>
          <span>•</span>
          <div className="flex items-center gap-1.5">
            <span className="material-symbols-outlined text-base text-primary">account_balance</span>
            <span>Nodal Authority: CPWD Northern Zone IV</span>
          </div>
        </div>
      </div>

      {/* Action indicators & Milestones */}
      <div className="flex items-stretch sm:items-center gap-3 flex-wrap lg:flex-nowrap">
        {/* Countdown Card */}
        <div className="flex-1 sm:flex-initial bg-surface-container-low px-4 py-2.5 rounded-xl flex items-center gap-3 border border-outline-variant/20">
          <div className="w-10 h-10 rounded-full bg-error-container text-on-error-container flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-xl">hourglass_top</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant">Bid Closing In</span>
            <span className="text-xs font-bold text-error leading-tight">3 Days 08h 42m</span>
          </div>
        </div>

        {/* EMD Exemption Status */}
        <div className="flex-1 sm:flex-initial bg-surface-container-low px-4 py-2.5 rounded-xl flex items-center gap-3 border border-outline-variant/20">
          <div className="w-10 h-10 rounded-full bg-secondary-fixed text-on-secondary-fixed flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              verified
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant">EMD Status</span>
            <span className="text-xs font-bold text-on-surface leading-tight">Exempt · Rule 153 GFR</span>
          </div>
        </div>
      </div>
    </section>
  );
}
