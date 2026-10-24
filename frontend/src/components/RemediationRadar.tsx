import React from "react";
import Link from "next/link";

export default function RemediationRadar() {
  return (
    <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-[0_12px_32px_-4px_rgba(59,0,102,0.06)] border border-outline-variant/30 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-secondary text-2xl">bolt</span>
          <h2 className="font-serif text-xl font-bold text-primary">Remediation Radar</h2>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed font-bold">
          Ranked
        </span>
      </div>

      <p className="text-xs text-on-surface-variant -mt-1 leading-snug">
        Prioritized actions to reach 95+ readiness score.
      </p>

      {/* Action Items List */}
      <div className="flex flex-col gap-3">
        {/* Priority 1 */}
        <div className="p-3.5 rounded-xl bg-surface-container-low hover:bg-surface-container border border-outline-variant/20 transition-colors flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1.5 text-[10px] font-bold text-error uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-error" />
              P1 • CSPO / NSIC
            </span>
            <span className="text-xs text-secondary font-bold">+8 pts</span>
          </div>
          <p className="text-xs font-bold text-on-surface">
            Upload Single Point NSIC Registration
          </p>
          <p className="text-xs text-on-surface-variant leading-snug">
            Required for CPWD tender to claim MSE EMD exemption.
          </p>
          <div className="flex items-center justify-end pt-0.5">
            <Link
              href="/audit"
              className="px-3 py-1 rounded-full bg-primary text-on-primary text-xs font-semibold hover:bg-primary-container transition-all shadow-sm"
            >
              Resolve
            </Link>
          </div>
        </div>

        {/* Priority 2 */}
        <div className="p-3.5 rounded-xl bg-surface-container-low hover:bg-surface-container border border-outline-variant/20 transition-colors flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1.5 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              P2 • NIC CODE
            </span>
            <span className="text-xs text-secondary font-bold">+4 pts</span>
          </div>
          <p className="text-xs font-bold text-on-surface">
            Confirm NIC Code 81210 Coverage
          </p>
          <p className="text-xs text-on-surface-variant leading-snug">
            Align Udyam certificate scope with mechanized cleaning clause.
          </p>
          <div className="flex items-center justify-end pt-0.5">
            <button className="px-3 py-1 rounded-full bg-surface-container-high text-on-surface text-xs font-semibold hover:bg-surface-container transition-all cursor-pointer border border-outline-variant/30">
              Validate
            </button>
          </div>
        </div>

        {/* Priority 3 */}
        <div className="p-3.5 rounded-xl bg-surface-container-low hover:bg-surface-container border border-outline-variant/20 transition-colors flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1.5 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-outline" />
              P3 • GST DELTA
            </span>
            <span className="text-xs text-on-surface-variant font-bold">+2 pts</span>
          </div>
          <p className="text-xs font-bold text-on-surface">
            Reconcile GST Turnover Delta (0.3%)
          </p>
          <p className="text-xs text-on-surface-variant leading-snug">
            Minor variance between GSTR-3B filings and audited balance sheet UDIN.
          </p>
          <div className="flex items-center justify-end pt-0.5">
            <button className="px-3 py-1 rounded-full bg-surface-container-high text-on-surface text-xs font-semibold hover:bg-surface-container transition-all cursor-pointer border border-outline-variant/30">
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
