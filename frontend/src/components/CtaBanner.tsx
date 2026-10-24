import React from "react";
import Link from "next/link";

export default function CtaBanner() {
  return (
    <section className="bg-brand-surface py-20 sm:py-28 px-4 sm:px-6 lg:px-8 text-center border-t border-indigo-100" data-purpose="cta-banner">
      <div className="max-w-3xl mx-auto">
        <h2 className="font-serif text-4xl sm:text-6xl text-brand-charcoal font-normal leading-tight">
          Your Next Opportunity <br />
          Starts Here.
        </h2>
        <p className="mt-4 text-base sm:text-lg text-brand-muted">
          Spend less time searching through obscure portals and more time preparing bids that win.
        </p>

        {/* Purple CTA Button */}
        <div className="mt-8 flex justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center pl-7 pr-3 py-3 text-base font-semibold text-white bg-brand-purple hover:bg-brand-hover rounded-full transition-all group shadow-md hover:shadow-lg hover:scale-102 cursor-pointer"
          >
            <span>Get Started Free</span>
            <span className="w-8 h-8 ml-3 rounded-full bg-white/20 group-hover:bg-white/30 flex items-center justify-center transition-colors">
              <svg className="w-4 h-4 text-white stroke-[2.5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
          </Link>
        </div>
      </div>
    </section>
  );
}
