"use client";

import React, { useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import DashboardHeader from "@/components/DashboardHeader";

interface TenderItem {
  id: string;
  refNo: string;
  portal: "GeM" | "CPPP" | "IREPS" | "State";
  title: string;
  dept: string;
  location: string;
  value: string;
  closingIn: string;
  closingUrgent?: boolean;
  matchScore: number;
  emdStatus: string;
  corrigendaCount: number;
  status: "Qualified" | "Action Req" | "Under Review";
}

export default function OpenTendersPage() {
  const [selectedPortal, setSelectedPortal] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState("");

  const tenders: TenderItem[] = [
    {
      id: "cpwd-718",
      refNo: "CPWD/NZ/EE(E)/2024/718",
      portal: "GeM",
      title: "Comprehensive Integrated Facility Management & Mechanized Operations",
      dept: "Central Public Works Department",
      location: "Shastri Bhawan Complex, New Delhi",
      value: "₹3.90 Cr",
      closingIn: "3d 14h",
      closingUrgent: false,
      matchScore: 94,
      emdStatus: "MSE Exempt Claimed",
      corrigendaCount: 2,
      status: "Qualified",
    },
    {
      id: "railways-99",
      refNo: "IREPS/NR/HK-2024-99",
      portal: "IREPS",
      title: "On-Board Mechanized Housekeeping Services (OBHS)",
      dept: "Northern Railway Division",
      location: "New Delhi Railway Division",
      value: "₹1.45 Cr",
      closingIn: "18h 20m",
      closingUrgent: true,
      matchScore: 72,
      emdStatus: "Exemption Pending CSPO",
      corrigendaCount: 1,
      status: "Action Req",
    },
    {
      id: "aiims-41",
      refNo: "CPPP/AIIMS-DELHI/2024/SAN-41",
      portal: "CPPP",
      title: "Specialized Hospital Bio-Sanitization & Environmental Sterilization",
      dept: "All India Institute of Medical Sciences",
      location: "Main Hospital Wing, Ansari Nagar",
      value: "₹85.0 Lakh",
      closingIn: "6d 02h",
      closingUrgent: false,
      matchScore: 98,
      emdStatus: "100% Verified Pass",
      corrigendaCount: 3,
      status: "Qualified",
    },
    {
      id: "mes-102",
      refNo: "GEM/2025/B/883102",
      portal: "GeM",
      title: "Military Engineer Services Command Hospital HVAC Retrofit",
      dept: "Ministry of Defence (MES)",
      location: "Chandimandir Military Cantonment",
      value: "₹5.20 Cr",
      closingIn: "8d 06h",
      closingUrgent: false,
      matchScore: 89,
      emdStatus: "Rule 153 GFR Eligible",
      corrigendaCount: 0,
      status: "Under Review",
    },
    {
      id: "nhai-04",
      refNo: "CPPP/2025/NHAI/04",
      portal: "CPPP",
      title: "Intelligent Highway Toll Infrastructure Maintenance & Operations",
      dept: "National Highways Authority of India",
      location: "Eastern Peripheral Expressway",
      value: "₹7.80 Cr",
      closingIn: "11d 19h",
      closingUrgent: false,
      matchScore: 86,
      emdStatus: "MSE Exemption Claimed",
      corrigendaCount: 4,
      status: "Qualified",
    },
  ];

  const filtered = tenders.filter((t) => {
    const matchesPortal = selectedPortal === "All" || t.portal === selectedPortal;
    const matchesSearch =
      searchQuery === "" ||
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.refNo.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.dept.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesPortal && matchesSearch;
  });

  return (
    <div className="bg-surface font-sans text-on-surface antialiased min-h-screen">
      <Sidebar activeTab="tenders" />

      <div className="lg:pl-72 flex flex-col min-h-screen">
        <DashboardHeader />

        <main className="w-full pt-16 bg-surface min-h-screen">
          <div className="px-4 sm:px-8 xl:px-12 py-8 flex flex-col gap-6 max-w-[1500px] mx-auto w-full pb-24">
            {/* Page Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] text-on-surface-variant uppercase tracking-widest block font-bold">
                  Central Indexation Stream
                </span>
                <h1 className="font-serif text-3xl sm:text-4xl font-bold text-primary">
                  Open Tenders Radar
                </h1>
                <p className="text-sm text-on-surface-variant mt-1">
                  Continuous live feeds from GeM, CPPP, IREPS &amp; 28 State Procurement portals.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <Link
                  href="/audit"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary text-on-primary text-xs font-bold shadow-sm hover:bg-primary-container transition-all"
                >
                  <span className="material-symbols-outlined text-base">verified</span>
                  <span>Run Bid Audit</span>
                </Link>
              </div>
            </div>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-surface-container-lowest neu-flat p-5 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant">Active Tracking</span>
                  <p className="font-serif text-2xl font-bold text-primary mt-0.5">14 Bids Live</p>
                </div>
                <div className="w-10 h-10 rounded-xl neu-flat-sm bg-secondary-fixed flex items-center justify-center text-on-secondary-fixed">
                  <span className="material-symbols-outlined text-xl">gavel</span>
                </div>
              </div>

              <div className="bg-surface-container-lowest neu-flat p-5 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant">Pipeline Volume</span>
                  <p className="font-serif text-2xl font-bold text-secondary mt-0.5">₹18.4 Cr</p>
                </div>
                <div className="w-10 h-10 rounded-xl neu-flat-sm bg-purple-50 flex items-center justify-center text-brand-purple">
                  <span className="material-symbols-outlined text-xl">account_balance_wallet</span>
                </div>
              </div>

              <div className="bg-surface-container-lowest neu-flat p-5 rounded-2xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant">Urgent Closures</span>
                  <p className="font-serif text-2xl font-bold text-error mt-0.5">4 Closing &lt;48h</p>
                </div>
                <div className="w-10 h-10 rounded-xl neu-flat-sm bg-error-container flex items-center justify-center text-on-error-container">
                  <span className="material-symbols-outlined text-xl">timer</span>
                </div>
              </div>
            </div>

            {/* Filter Bar */}
            <div className="bg-surface-container-lowest neu-flat p-4 sm:p-5 rounded-2xl flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
              {/* Portal Selector Tabs */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
                {["All", "GeM", "CPPP", "IREPS", "State"].map((portal) => (
                  <button
                    key={portal}
                    onClick={() => setSelectedPortal(portal)}
                    className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                      selectedPortal === portal
                        ? "neu-button-primary font-semibold"
                        : "neu-button text-on-surface-variant"
                    }`}
                  >
                    {portal}
                  </button>
                ))}
              </div>

              {/* Search input */}
              <div className="relative flex-1 max-w-md">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">
                  search
                </span>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Filter by keyword, Ref ID, department..."
                  className="w-full pl-10 pr-4 py-2.5 neu-pressed rounded-xl text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:ring-1 focus:ring-secondary/30 transition-all"
                />
              </div>
            </div>

            {/* Tenders Table / Card Grid */}
            <div className="flex flex-col gap-4">
              {filtered.map((tender) => (
                <div
                  key={tender.id}
                  className="bg-surface-container-lowest neu-flat rounded-2xl p-5 sm:p-6 hover:-translate-y-0.5 transition-all flex flex-col gap-4"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
                    <div className="flex items-start gap-3.5">
                      <div className="w-11 h-11 rounded-xl bg-surface-container-high text-primary flex items-center justify-center shrink-0 shadow-xs">
                        <span className="material-symbols-outlined text-2xl">
                          {tender.portal === "IREPS" ? "train" : tender.portal === "CPPP" ? "local_hospital" : "corporate_fare"}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-surface-container text-on-surface-variant font-mono font-medium">
                            {tender.refNo}
                          </span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                            tender.portal === "GeM"
                              ? "bg-secondary-fixed text-on-secondary-fixed"
                              : tender.portal === "IREPS"
                              ? "bg-amber-100 text-amber-900"
                              : "bg-blue-100 text-blue-900"
                          }`}>
                            {tender.portal} Portal
                          </span>
                          <span className={`text-[10px] font-bold flex items-center gap-1 ${
                            tender.closingUrgent ? "text-error" : "text-on-surface-variant"
                          }`}>
                            <span className="material-symbols-outlined text-sm">timer</span> Closes in {tender.closingIn}
                          </span>
                        </div>
                        <h3 className="font-serif text-lg sm:text-xl font-bold text-primary mt-1">
                          {tender.title}
                        </h3>
                        <p className="text-xs text-on-surface-variant">
                          {tender.dept} • {tender.location}
                        </p>
                      </div>
                    </div>

                    <div className="flex lg:flex-col items-center lg:items-end justify-between lg:justify-center shrink-0 border-t lg:border-t-0 pt-2 lg:pt-0 border-gray-100">
                      <span className="font-serif text-2xl font-bold text-primary">{tender.value}</span>
                      <span className="text-[10px] uppercase tracking-wider text-on-surface-variant font-semibold">
                        Estimated Value
                      </span>
                    </div>
                  </div>

                  {/* Badges Ribbon - Neumorphic Inset */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 p-3 rounded-xl neu-pressed text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-on-surface-variant text-[11px]">Match Score:</span>
                      <span className={`font-bold ${
                        tender.matchScore >= 90 ? "text-secondary font-serif text-base" : "text-error font-serif text-base"
                      }`}>
                        {tender.matchScore}% Qualified
                      </span>
                    </div>
                    <div className="flex items-center justify-between border-t sm:border-t-0 sm:border-l border-white/60 pt-1.5 sm:pt-0 sm:pl-3">
                      <span className="text-on-surface-variant text-[11px]">EMD Exemption:</span>
                      <span className="font-semibold text-on-surface truncate">{tender.emdStatus}</span>
                    </div>
                    <div className="flex items-center justify-between border-t sm:border-t-0 sm:border-l border-white/60 pt-1.5 sm:pt-0 sm:pl-3">
                      <span className="text-on-surface-variant text-[11px]">Corrigenda:</span>
                      <Link href="/corrigendum" className="font-bold text-secondary hover:underline">
                        {tender.corrigendaCount} Logged
                      </Link>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-xs text-on-surface-variant">
                      Status: <strong className="text-primary">{tender.status}</strong>
                    </span>
                    <div className="flex items-center gap-2">
                      <Link
                        href="/audit"
                        className="px-4 py-1.5 rounded-full neu-button-primary text-xs font-bold flex items-center gap-1"
                      >
                        <span>Audit Verdict</span>
                        <span className="material-symbols-outlined text-base">chevron_right</span>
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
