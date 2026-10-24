import React from "react";

export default function EvidenceInspector() {
  return (
    <section className="bg-surface-container-lowest neu-flat rounded-2xl p-6 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-wider text-secondary font-bold">
            Evidence Inspector
          </span>
          <h3 className="font-serif text-2xl text-primary mt-1 font-bold">
            Autonomous Extraction Snippet
          </h3>
        </div>
        <span className="text-[10px] neu-flat-sm bg-secondary-fixed text-on-secondary-fixed px-2.5 py-0.5 rounded-full font-bold">
          99.4% Match
        </span>
      </div>

      {/* Evidence Card */}
      <div className="neu-pressed rounded-2xl p-4 sm:p-5 flex flex-col gap-3 relative overflow-hidden">
        <div className="flex items-center justify-between text-on-surface-variant text-[10px] font-mono uppercase tracking-wider font-semibold">
          <span>Doc: CA_Audited_Turnover_FY24.pdf</span>
          <span>Page 2 · Clause 3.1</span>
        </div>

        {/* Mock Document OCR visual container */}
        <div className="bg-surface-container-lowest p-3 rounded-xl shadow-inner text-xs text-on-surface space-y-2 border border-outline-variant/20">
          <div className="flex items-center justify-between pb-1 bg-surface-container-low/50 px-2.5 py-1 rounded-lg">
            <span className="text-on-surface-variant font-medium">UDIN Registry Query:</span>
            <span className="text-secondary font-bold flex items-center gap-1">
              <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>
                check_circle
              </span>
              24098231BGJKP8812 (ICAI Verified)
            </span>
          </div>

          <div className="p-3 bg-secondary-fixed/20 rounded-lg border-l-2 border-secondary font-mono text-xs leading-relaxed">
            <span className="text-on-surface-variant block text-[10px] uppercase font-bold mb-1">
              Extracted Excerpt:
            </span>
            &ldquo;This is to certify that M/s ABC Facility Services Pvt Ltd achieved an aggregate annual turnover of{" "}
            <mark className="bg-secondary-fixed text-on-secondary-fixed px-1.5 py-0.5 rounded font-bold">
              INR 1,82,45,000/-
            </mark>{" "}
            (Rupees One Crore Eighty Two Lakhs Forty Five Thousand) from facility management activities during FY 2023-24...&rdquo;
          </div>
        </div>

        {/* Confidence & Accountant Meta */}
        <div className="grid grid-cols-2 gap-2 text-on-surface-variant text-xs mt-1">
          <div className="bg-surface-container p-2.5 rounded-xl flex flex-col">
            <span className="text-[10px] text-on-surface-variant font-medium">Confidence Rating</span>
            <span className="text-xs text-primary font-bold mt-0.5">High (Deterministic)</span>
          </div>
          <div className="bg-surface-container p-2.5 rounded-xl flex flex-col">
            <span className="text-[10px] text-on-surface-variant font-medium">Chartered Acc.</span>
            <span className="text-xs text-primary font-bold mt-0.5">S. Mehta &amp; Co (FCA)</span>
          </div>
        </div>
      </div>

      {/* Corroboration Engine status */}
      <div className="p-3.5 bg-surface-container-low rounded-xl flex items-center gap-3 border border-outline-variant/20">
        <span className="material-symbols-outlined text-secondary text-2xl">sync_saved_locally</span>
        <div className="flex flex-col">
          <span className="text-xs font-bold text-on-surface">Auto-Corroborated with Income Tax Portal</span>
          <span className="text-xs text-on-surface-variant leading-snug">
            ITR-6 Form FY24 matches exact turnover value. Zero discrepancy found.
          </span>
        </div>
      </div>

      {/* Action Button */}
      <button
        className="w-full bg-surface-container-low text-on-surface py-2.5 rounded-full text-xs font-bold flex items-center justify-center gap-2 hover:bg-surface-container-high transition-all cursor-pointer border border-outline-variant/30"
        type="button"
      >
        <span className="material-symbols-outlined text-base">visibility</span>
        <span>Open Full Verification Inspector</span>
      </button>
    </section>
  );
}
