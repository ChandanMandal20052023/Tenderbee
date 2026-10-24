import React from "react";

export default function RegulatoryBento() {
  return (
    <div className="bg-tertiary text-on-tertiary rounded-2xl p-6 shadow-sm border border-outline/30 flex flex-col justify-between relative overflow-hidden h-full">
      {/* Ambient decorative tint inside parent */}
      <div className="absolute -right-12 -bottom-12 w-48 h-48 bg-secondary-container/20 rounded-full blur-3xl pointer-events-none" />

      <div>
        <div className="flex items-center justify-between">
          <span className="text-[10px] tracking-widest uppercase text-tertiary-fixed-dim font-bold">
            Regulatory Validation
          </span>
          <span className="material-symbols-outlined text-tertiary-fixed-dim text-lg">policy</span>
        </div>
        <h3 className="font-serif text-2xl text-surface-bright mt-2 font-bold">
          GFR 2017 &amp; GeM GTC v4
        </h3>
        <p className="text-xs text-on-tertiary-container mt-1.5 leading-relaxed">
          Autonomous rule engine evaluated 42 specific tender clauses across CPWD manual stipulations.
        </p>
      </div>

      <div className="space-y-2.5 my-6">
        <div className="flex items-center justify-between py-1.5 bg-tertiary-container/60 px-3.5 rounded-xl border border-white/5">
          <span className="text-xs text-surface-bright font-medium">GFR Rule 153 MII Clause</span>
          <span className="text-[10px] bg-secondary-container px-2 py-0.5 rounded-full text-on-secondary-container font-bold">
            100% Pass
          </span>
        </div>
        <div className="flex items-center justify-between py-1.5 bg-tertiary-container/60 px-3.5 rounded-xl border border-white/5">
          <span className="text-xs text-surface-bright font-medium">GeM Turnover Ratio (3 Yrs)</span>
          <span className="text-[10px] bg-secondary-container px-2 py-0.5 rounded-full text-on-secondary-container font-bold">
            151.6% Excess
          </span>
        </div>
        <div className="flex items-center justify-between py-1.5 bg-tertiary-container/60 px-3.5 rounded-xl border border-white/5">
          <span className="text-xs text-surface-bright font-medium">Blacklist / Debarment Cross-Ref</span>
          <span className="text-[10px] bg-secondary-container px-2 py-0.5 rounded-full text-on-secondary-container font-bold">
            Zero Hits
          </span>
        </div>
      </div>

      <button
        className="w-full neu-button-primary py-2.5 px-4 rounded-full text-xs font-bold flex items-center justify-center gap-2 cursor-pointer"
        type="button"
      >
        <span>Inspect Rule Engine Traces</span>
        <span className="material-symbols-outlined text-base">arrow_forward</span>
      </button>
    </div>
  );
}
