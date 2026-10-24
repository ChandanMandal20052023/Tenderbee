"use client";

import React, { useState } from "react";

export default function AuditBottomBar() {
  const [reAuditing, setReAuditing] = useState(false);

  const handleReAudit = () => {
    setReAuditing(true);
    setTimeout(() => {
      setReAuditing(false);
    }, 1500);
  };

  return (
    <div className="bg-white/95 backdrop-blur-md rounded-2xl p-4 sm:p-5 shadow-[0_16px_40px_-10px_rgba(29,0,55,0.18)] border border-purple-100 flex flex-col md:flex-row items-center justify-between gap-4 sticky bottom-4 z-30 transition-all">
      {/* Status Warning Info */}
      <div className="flex items-center gap-3.5">
        <div className="w-11 h-11 rounded-full bg-primary flex items-center justify-center text-on-primary shrink-0 shadow-sm">
          <span className="material-symbols-outlined text-xl">lock</span>
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-serif text-lg sm:text-xl text-primary font-bold">
              Envelope Lock: 2 Blockers Remaining
            </span>
            <span className="text-[10px] bg-error-container text-on-error-container px-2.5 py-0.5 rounded-full font-bold">
              Not Ready
            </span>
          </div>
          <span className="text-xs text-on-surface-variant leading-snug mt-0.5">
            Resolve statutory CSPO attachment and affirm mechanized cleaning scope to reach the required 95/100 threshold.
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3 w-full md:w-auto flex-wrap sm:flex-nowrap shrink-0">
        <button
          onClick={handleReAudit}
          className="flex-1 sm:flex-initial bg-surface-container-low text-on-surface px-4 py-2.5 rounded-full text-xs font-bold flex items-center justify-center gap-2 hover:bg-surface-container transition-all cursor-pointer border border-outline-variant/30 active:scale-98"
          type="button"
        >
          <span className={`material-symbols-outlined text-base ${reAuditing ? "animate-spin" : ""}`}>
            refresh
          </span>
          <span>{reAuditing ? "Auditing Engine..." : "Run Final Re-Audit"}</span>
        </button>

        <button
          className="flex-1 sm:flex-initial bg-primary text-on-primary px-5 py-2.5 rounded-full text-xs font-bold flex items-center justify-center gap-2 hover:bg-primary-container transition-all shadow-md hover:shadow-lg cursor-pointer active:scale-98"
          type="button"
        >
          <span className="material-symbols-outlined text-base">description</span>
          <span>Generate Compliance Dossier</span>
          <span className="w-6 h-6 rounded-full bg-secondary text-on-secondary flex items-center justify-center ml-1">
            <span className="material-symbols-outlined text-sm">arrow_forward</span>
          </span>
        </button>
      </div>
    </div>
  );
}
