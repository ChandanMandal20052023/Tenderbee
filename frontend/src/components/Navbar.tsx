"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-100" data-purpose="site-header">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo with Official public/logo.png */}
        <Link href="/" aria-label="TenderBee Home" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl overflow-hidden flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform shadow-xs">
            <Image
              src="/logo.png"
              alt="TenderBee Logo"
              width={36}
              height={36}
              className="w-full h-full object-contain"
              priority
            />
          </div>
          <span className="font-serif text-2xl font-bold tracking-tight text-primary">
            Tender<span className="text-secondary">Bee</span>
          </span>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center space-x-7 text-sm font-medium text-brand-charcoal/90">
          <Link href="/dashboard" className="relative group cursor-pointer flex items-center gap-1 hover:text-brand-purple transition-colors">
            <span>Platform</span>
            <svg className="w-4 h-4 opacity-60 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
            </svg>
          </Link>
          <Link href="/tenders" className="relative group cursor-pointer flex items-center gap-1 hover:text-brand-purple transition-colors">
            <span>Solutions</span>
            <svg className="w-4 h-4 opacity-60 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
            </svg>
          </Link>
          <Link href="/audit" className="relative group cursor-pointer flex items-center gap-1 hover:text-brand-purple transition-colors">
            <span>How It Works</span>
            <svg className="w-4 h-4 opacity-60 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
            </svg>
          </Link>
          <Link href="/vault" className="relative group cursor-pointer flex items-center gap-1 hover:text-brand-purple transition-colors">
            <span>Resources</span>
            <svg className="w-4 h-4 opacity-60 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
            </svg>
          </Link>
          <Link className="hover:text-brand-purple transition-colors" href="/corrigendum">
            Plans
          </Link>
        </nav>

        {/* Desktop Action Buttons */}
        <div className="hidden sm:flex items-center space-x-3">
          <Link
            href="/dashboard"
            className="px-4 py-2 text-xs sm:text-sm font-semibold text-brand-charcoal border border-gray-300 rounded-full hover:bg-gray-50 transition-colors"
          >
            Log in
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center pl-5 pr-2 py-1.5 sm:py-2 text-xs sm:text-sm font-semibold text-white bg-brand-purple hover:bg-brand-hover rounded-full transition-all group shadow-sm hover:shadow"
          >
            <span>Get started</span>
            <span className="w-7 h-7 sm:w-8 sm:h-8 ml-2 rounded-full bg-white/20 group-hover:bg-white/30 flex items-center justify-center transition-colors">
              <svg className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white stroke-[2.5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
          </Link>
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-gray-700 hover:text-brand-purple transition-colors"
          aria-label="Toggle mobile menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {mobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-gray-100 px-4 pt-2 pb-6 space-y-3">
          <div className="flex flex-col space-y-2 text-sm font-medium text-brand-charcoal">
            <Link href="/dashboard" className="py-2 border-b border-gray-50">Dashboard</Link>
            <Link href="/tenders" className="py-2 border-b border-gray-50">Open Tenders</Link>
            <Link href="/audit" className="py-2 border-b border-gray-50">Bid Audits</Link>
            <Link href="/vault" className="py-2 border-b border-gray-50">Document Vault</Link>
            <Link href="/corrigendum" className="py-2">Corrigenda</Link>
          </div>
          <div className="pt-2 flex flex-col gap-2">
            <Link
              href="/dashboard"
              className="w-full text-center py-2 text-sm font-semibold text-brand-charcoal border border-gray-300 rounded-full"
            >
              Log in
            </Link>
            <Link
              href="/dashboard"
              className="w-full inline-flex items-center justify-center py-2 text-sm font-semibold text-white bg-brand-purple rounded-full"
            >
              Get started
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
