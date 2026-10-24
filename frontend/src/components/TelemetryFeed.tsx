import React from "react";

export default function TelemetryFeed() {
  const telemetryItems = [
    {
      title: "ICAI UDIN VERIFIED",
      time: "14:02:11 IST",
      description: "UDIN 23491823BK checked against MCA & ICAI registry. CA firm credentials validated.",
    },
    {
      title: "SHA-256 HASH COMPLIANT",
      time: "13:58:44 IST",
      description: "Doc integrity: e7f90c8...3b92 matches vault master record.",
    },
    {
      title: "CBDT PAN MATCHED",
      time: "13:42:09 IST",
      description: "PAN AAACF9182K matched to ABC Facility Services LLP. No debarment tags found on GeM blacklist.",
    },
    {
      title: "PORTAL SYNC HEARTBEAT",
      time: "13:30:00 IST",
      description: "CPPP XML Feed endpoint parsed: 124 new NIT notices analyzed for scope match.",
    },
  ];

  return (
    <div className="bg-surface-container-lowest rounded-2xl p-6 shadow-[0_12px_32px_-4px_rgba(59,0,102,0.06)] border border-outline-variant/30 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-secondary animate-pulse" />
          <h2 className="font-serif text-xl font-bold text-primary">Telemetry Feed</h2>
        </div>
        <span className="text-[10px] font-mono text-on-surface-variant uppercase tracking-wider font-semibold">
          LIVE STREAM
        </span>
      </div>

      {/* Feed Items */}
      <div className="flex flex-col gap-2.5 font-mono text-xs">
        {telemetryItems.map((item, idx) => (
          <div
            key={idx}
            className="p-3 rounded-xl bg-surface-container-low border border-outline-variant/20 flex flex-col gap-1 hover:bg-surface-container transition-colors"
          >
            <div className="flex items-center justify-between text-on-surface-variant">
              <span className="text-secondary font-bold text-[10px] tracking-wide">{item.title}</span>
              <span className="text-[10px] text-on-surface-variant font-medium">{item.time}</span>
            </div>
            <p className="text-on-surface text-xs leading-snug truncate">{item.description}</p>
          </div>
        ))}
      </div>

      {/* Security Protocol Footer */}
      <div className="pt-2 text-center border-t border-outline-variant/20">
        <span className="text-[9px] uppercase tracking-widest text-on-surface-variant font-semibold">
          Encrypted with 2048-bit Class 3 DSC Protocol
        </span>
      </div>
    </div>
  );
}
