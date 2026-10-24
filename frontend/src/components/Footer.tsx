import React from "react";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-brand-eggplant text-white pt-20 pb-12 px-4 sm:px-6 lg:px-8 border-t border-purple-950" data-purpose="site-footer">
      <div className="max-w-7xl mx-auto">
        {/* Multi-Column Directory */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8 pb-16 border-b border-purple-900/60 text-xs sm:text-sm">
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-xs mb-4">Product</h4>
            <ul className="space-y-2.5 text-purple-200/70">
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Tender Search</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/audit">Eligibility Engine</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Corrigendum Radar</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/audit">Checklist Builder</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">BOQ Estimator</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Consortium Matching</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-xs mb-4">Platform</h4>
            <ul className="space-y-2.5 text-purple-200/70">
              <li><Link className="hover:text-white transition-colors" href="/dashboard">TenderBee AI ✨</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Udyam Verification</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">TenderBee API</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Integrations</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">What&apos;s New</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-xs mb-4">Solutions</h4>
            <ul className="space-y-2.5 text-purple-200/70">
              <li><Link className="hover:text-white transition-colors" href="/dashboard">MSMEs & Startups</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Civil & EPC Contractors</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">IT & Services Vendors</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Enterprise Bidders</Link></li>
              <li><Link className="hover:text-white transition-colors" href="/dashboard">Bid Consultants</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-xs mb-4">Resources</h4>
            <ul className="space-y-2.5 text-purple-200/70">
              <li><a className="hover:text-white transition-colors" href="#guidebook">Tender Guidebook</a></li>
              <li><a className="hover:text-white transition-colors" href="#emd">EMD Exemption Rules</a></li>
              <li><a className="hover:text-white transition-colors" href="#calculator">Turnover Calculator</a></li>
              <li><a className="hover:text-white transition-colors" href="#corrigendum">Corrigendum Tracker</a></li>
              <li><a className="hover:text-white transition-colors" href="#events">Webinars & Events</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider text-xs mb-4">Company</h4>
            <ul className="space-y-2.5 text-purple-200/70">
              <li><a className="hover:text-white transition-colors" href="#about">About Us</a></li>
              <li>
                <a className="hover:text-white transition-colors inline-flex items-center gap-1.5" href="#careers">
                  <span>Careers</span>
                  <span className="px-1.5 py-0.5 text-[9px] font-bold bg-amber-400 text-black rounded leading-none">HIRING</span>
                </a>
              </li>
              <li><a className="hover:text-white transition-colors" href="#security">Security & Privacy</a></li>
              <li><a className="hover:text-white transition-colors" href="#status">System Status</a></li>
              <li><a className="hover:text-white transition-colors" href="#support">Contact Support</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom Trademark & Legal Line */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-purple-300/60">
          <p>© 2025 TenderBee Technologies Inc. All rights reserved.</p>
          <div className="mt-4 sm:mt-0 flex space-x-6">
            <a className="hover:text-white transition-colors" href="#privacy">Privacy Policy</a>
            <a className="hover:text-white transition-colors" href="#terms">Terms of Service</a>
            <a className="hover:text-white transition-colors" href="#cookies">Cookie Settings</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
