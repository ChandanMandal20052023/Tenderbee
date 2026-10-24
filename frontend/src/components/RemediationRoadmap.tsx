"use client";

import React, { useState } from "react";

export default function RemediationRoadmap() {
  const [attached, setAttached] = useState(false);
  const [signed, setSigned] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);

  return (
    <section className="bg-surface-container-lowest rounded-2xl p-6 shadow-sm border border-outline-variant/30 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <span className="text-[10px] uppercase tracking-wider text-secondary font-bold">
            Priority Fixes
          </span>
          <h3 className="font-serif text-2xl text-primary mt-1 font-bold">
            Ranked Remediation Roadmap
          </h3>
        </div>
        <span className="text-xs font-semibold bg-surface-container px-3 py-1 rounded-full text-on-surface-variant border border-outline-variant/30">
          {attached && signed ? "All Tasks Cleared" : `${2 - (attached ? 1 : 0) - (signed ? 1 : 0)} Tasks to Unlock`}
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {/* Critical Item 1 */}
        <div className="bg-surface-container-low p-4 sm:p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all border border-outline-variant/20">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-error text-on-error flex items-center justify-center shrink-0 mt-0.5 font-bold text-sm shadow-sm">
              {attached ? "✓" : "!"}
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-bold text-on-surface">
                  Upload CSPO or NSIC Competency Certificate
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                  attached ? "bg-emerald-100 text-emerald-800" : "bg-error-container text-on-error-container"
                }`}>
                  {attached ? "Attached (+8 PTS)" : "Blocker (+8 PTS)"}
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mt-1 leading-snug">
                Required by GeM Bid Document Section 4.2.1. Validates exemption from prior turnover/experience conditions for facility management tenders.
              </p>
              <span className="text-[10px] text-on-surface-variant font-mono mt-2 font-medium">
                Vault Match: NSIC_Technical_2024.pdf (Exp: 2026) exists in Master Vault
              </span>
            </div>
          </div>
          <div className="flex sm:flex-col items-center gap-2 shrink-0 self-end sm:self-center">
            <button
              onClick={() => setAttached(!attached)}
              className={`w-full px-4 py-2 rounded-full text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm transition-all cursor-pointer ${
                attached
                  ? "bg-emerald-600 text-white"
                  : "bg-primary text-on-primary hover:bg-primary-container"
              }`}
              type="button"
            >
              <span className="material-symbols-outlined text-base">
                {attached ? "check_circle" : "upload_file"}
              </span>
              <span>{attached ? "Attached" : "Attach Now"}</span>
            </button>
          </div>
        </div>

        {/* Warning Item 2 */}
        <div className="bg-surface-container-low p-4 sm:p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all border border-outline-variant/20">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-secondary-fixed text-on-secondary-fixed flex items-center justify-center shrink-0 mt-0.5 font-bold text-sm shadow-sm">
              {signed ? "✓" : "2"}
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-bold text-on-surface">
                  Mechanized Cleaning Scope Affirmation
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                  signed ? "bg-emerald-100 text-emerald-800" : "bg-secondary-fixed text-on-secondary-fixed"
                }`}>
                  {signed ? "Signed (+4 PTS)" : "Warning (+4 PTS)"}
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mt-1 leading-snug">
                Your registered NIC code is 81210 (General Cleaning). CPWD requires self-declaration of mechanized scrubbing and high-reach facade equipment availability.
              </p>
              <span className="text-[10px] text-on-surface-variant font-mono mt-2 font-medium">
                Auto-drafted Form Annexure-IV ready for DSC signature
              </span>
            </div>
          </div>
          <div className="flex sm:flex-col items-center gap-2 shrink-0 self-end sm:self-center">
            <button
              onClick={() => setSigned(!signed)}
              className={`w-full px-4 py-2 rounded-full text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm transition-all cursor-pointer border ${
                signed
                  ? "bg-secondary text-on-secondary border-secondary"
                  : "bg-surface-container-lowest text-on-surface hover:bg-surface-container border-outline-variant/30"
              }`}
              type="button"
            >
              <span className="material-symbols-outlined text-base">
                {signed ? "check_circle" : "edit_document"}
              </span>
              <span>{signed ? "Affirmed" : "Review & Sign"}</span>
            </button>
          </div>
        </div>

        {/* Advisory Item 3 */}
        <div className="bg-surface-container-low/60 p-4 sm:p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-outline-variant/20">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-surface-container text-on-surface-variant flex items-center justify-center shrink-0 mt-0.5 font-bold text-sm">
              {acknowledged ? "✓" : "3"}
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs sm:text-sm font-bold text-on-surface">
                  Corrigendum #2 Acknowledgement
                </span>
                <span className="text-[10px] bg-surface-container text-on-surface-variant px-2 py-0.5 rounded-full font-bold">
                  {acknowledged ? "Acknowledged" : "Advisory"}
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mt-1 leading-snug">
                Corrigendum released 14 hrs ago modified wage schedules under Minimum Wages Act (Delhi NCT). Verified against payroll model.
              </p>
            </div>
          </div>
          <div className="shrink-0 self-end sm:self-center">
            <button
              onClick={() => setAcknowledged(!acknowledged)}
              className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer border ${
                acknowledged
                  ? "bg-surface-container-highest text-primary border-primary/20"
                  : "bg-surface-container text-on-surface hover:bg-surface-container-high border-outline-variant/20"
              }`}
              type="button"
            >
              <span className="material-symbols-outlined text-base">done_all</span>
              <span>{acknowledged ? "Done" : "Acknowledge"}</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
