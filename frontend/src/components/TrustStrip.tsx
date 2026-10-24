import React from "react";

export default function TrustStrip() {
  const portals = [
    { name: "GeM", dot: true, bold: true },
    { name: "CPPP / eProcure", bold: false },
    { name: "IREPS", uppercase: true, bold: true },
    { name: "Defence eProcurement", bold: false },
    { name: "CPWD e-Tendering", bold: false },
    { name: "PMGSY", uppercase: true, bold: true },
    { name: "State eProcurement (GePNIC)", bold: false },
    { name: "Municipal e-Tendering", bold: false },
  ];

  return (
    <section className="py-12 bg-white border-b border-gray-100" data-purpose="social-proof-strip">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p className="text-xs font-semibold tracking-wider text-gray-500 uppercase">
          Explore tenders, verify compliance, and bid with confidence—powered by TenderBee.
        </p>

        {/* Minimalist Monochrome Partner Brand Logotypes Continuous Ticker */}
        <div className="mt-8 relative w-full overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_10%,black_90%,transparent)]">
          <div className="animate-ticker items-center py-2">
            {/* Primary Track */}
            <div className="flex items-center space-x-8 sm:space-x-12 pr-8 sm:pr-12 text-gray-800">
              {portals.map((p, i) => (
                <React.Fragment key={`portal-1-${i}`}>
                  <span
                    className={`flex items-center gap-2 text-sm sm:text-base ${
                      p.bold ? "font-bold text-gray-900" : "font-semibold text-gray-700"
                    } ${p.uppercase ? "uppercase tracking-widest text-base sm:text-lg" : "tracking-tight"}`}
                  >
                    {p.dot && <span className="w-1.5 h-1.5 rounded-full bg-brand-purple" />}
                    {p.name}
                  </span>
                  <span className="text-gray-300">•</span>
                </React.Fragment>
              ))}
            </div>

            {/* Seamless Cloned Track */}
            <div className="flex items-center space-x-8 sm:space-x-12 pr-8 sm:pr-12 text-gray-800" aria-hidden="true">
              {portals.map((p, i) => (
                <React.Fragment key={`portal-2-${i}`}>
                  <span
                    className={`flex items-center gap-2 text-sm sm:text-base ${
                      p.bold ? "font-bold text-gray-900" : "font-semibold text-gray-700"
                    } ${p.uppercase ? "uppercase tracking-widest text-base sm:text-lg" : "tracking-tight"}`}
                  >
                    {p.dot && <span className="w-1.5 h-1.5 rounded-full bg-brand-purple" />}
                    {p.name}
                  </span>
                  <span className="text-gray-300">•</span>
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
