"use client";

import React, { useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import DashboardHeader from "@/components/DashboardHeader";

interface CorrigendumItem {
  id: string;
  tenderRef: string;
  tenderTitle: string;
  dept: string;
  corrigendumNo: string;
  publishedAt: string;
  severity: "Critical" | "Important" | "Notice";
  changeType: "Date Extension" | "BOQ / Price Revision" | "Eligibility Relaxation" | "Technical Clarification";
  impactSummary: string;
  before: string;
  after: string;
  reAuditRecommended: boolean;
  bidStatus: "Drafting" | "Submitted" | "Action Pending";
}

export default function CorrigendumRadarPage() {
  const [selectedFilter, setSelectedFilter] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [reviewedItems, setReviewedItems] = useState<Record<string, boolean>>({});

  const corrigenda: CorrigendumItem[] = [
    {
      id: "corr-1",
      tenderRef: "CPWD/NZ/EE(E)/2024/718",
      tenderTitle: "Comprehensive Integrated Facility Management & Mechanized Operations",
      dept: "Central Public Works Department",
      corrigendumNo: "Corrigendum No. 2 (Addendum #2)",
      publishedAt: "2 hours ago (24 Oct 2024, 14:30 IST)",
      severity: "Critical",
      changeType: "Date Extension",
      impactSummary: "Bid submission deadline pushed by 5 days due to festival holiday requests from bidders.",
      before: "Closing Date: 28 Oct 2024, 15:00 IST | Technical Bid Opening: 29 Oct 2024, 15:30 IST",
      after: "Closing Date: 02 Nov 2024, 15:00 IST | Technical Bid Opening: 03 Nov 2024, 15:30 IST",
      reAuditRecommended: false,
      bidStatus: "Drafting",
    },
    {
      id: "corr-2",
      tenderRef: "CPWD/NZ/EE(E)/2024/718",
      tenderTitle: "Comprehensive Integrated Facility Management & Mechanized Operations",
      dept: "Central Public Works Department",
      corrigendumNo: "Corrigendum No. 1",
      publishedAt: "Yesterday (23 Oct 2024, 11:15 IST)",
      severity: "Critical",
      changeType: "Eligibility Relaxation",
      impactSummary: "Average annual turnover requirement relaxed from ₹2.50 Cr down to ₹1.80 Cr to encourage MSME participation.",
      before: "Minimum Annual Turnover required: ₹2.50 Crore during last 3 financial years",
      after: "Revised Minimum Annual Turnover: ₹1.80 Crore during last 3 financial years (UDIN verified)",
      reAuditRecommended: true,
      bidStatus: "Drafting",
    },
    {
      id: "corr-3",
      tenderRef: "IREPS/NR/HK-2024-99",
      tenderTitle: "On-Board Mechanized Housekeeping Services (OBHS)",
      dept: "Northern Railway Division",
      corrigendumNo: "Corrigendum No. 1",
      publishedAt: "5 hours ago (24 Oct 2024, 11:45 IST)",
      severity: "Important",
      changeType: "BOQ / Price Revision",
      impactSummary: "Schedule of Rates item #14 (Eco-friendly enzymatic cleaning agent) revised specification code.",
      before: "Item #14: Industrial Disinfectant Grade A (IS:1061 compliant)",
      after: "Item #14: Bio-enzymatic Organic Surface Cleaner (CPCB approved eco-grade)",
      reAuditRecommended: true,
      bidStatus: "Action Pending",
    },
    {
      id: "corr-4",
      tenderRef: "AIIMS/FAC/2024/41",
      tenderTitle: "Annual Maintenance Contract for Bio-Medical Waste Handling & Sterilization",
      dept: "All India Institute of Medical Sciences",
      corrigendumNo: "Clarification Addendum #1",
      publishedAt: "1 day ago (23 Oct 2024, 17:00 IST)",
      severity: "Notice",
      changeType: "Technical Clarification",
      impactSummary: "Pre-bid meeting queries answered regarding incinerator ash testing protocols and manifest uploading.",
      before: "Clause 4.2: Standard CPCB manifest submission within 48 hours",
      after: "Clause 4.2: Real-time digital manifest sync on DPCC barcoded tracking portal",
      reAuditRecommended: false,
      bidStatus: "Drafting",
    },
    {
      id: "corr-5",
      tenderRef: "DMRC/HK/2024/88",
      tenderTitle: "Housekeeping & Facility Management Services at Yellow Line Elevated Stations",
      dept: "Delhi Metro Rail Corporation",
      corrigendumNo: "Corrigendum No. 3",
      publishedAt: "2 days ago (22 Oct 2024, 16:15 IST)",
      severity: "Critical",
      changeType: "Date Extension",
      impactSummary: "Mandatory site visit window extended by 3 working days for station inspection clearances.",
      before: "Joint Inspection Certificate mandatory date: 24 Oct 2024",
      after: "Joint Inspection Certificate extended date: 28 Oct 2024 (Station Controller counter-sign)",
      reAuditRecommended: true,
      bidStatus: "Drafting",
    },
  ];

  const filterOptions = ["All", "Critical", "Date Extension", "Eligibility", "BOQ Revision"];

  const filteredItems = corrigenda.filter((item) => {
    const matchesFilter =
      selectedFilter === "All" ||
      (selectedFilter === "Critical" && item.severity === "Critical") ||
      (selectedFilter === "Date Extension" && item.changeType === "Date Extension") ||
      (selectedFilter === "Eligibility" && item.changeType === "Eligibility Relaxation") ||
      (selectedFilter === "BOQ Revision" && item.changeType === "BOQ / Price Revision");

    const matchesSearch =
      item.tenderTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tenderRef.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.dept.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.impactSummary.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  const toggleReview = (id: string) => {
    setReviewedItems((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="bg-surface font-sans text-on-surface antialiased min-h-screen">
      {/* Sidebar */}
      <Sidebar activeTab="corrigendum" />

      {/* Main Workspace */}
      <div className="lg:pl-72 flex flex-col min-h-screen">
        {/* Top Header */}
        <DashboardHeader />

        {/* Content Container */}
        <main className="w-full pt-16 bg-surface min-h-screen">
          <div className="px-4 sm:px-8 xl:px-12 py-8 flex flex-col gap-6 max-w-[1500px] mx-auto w-full pb-24">
            {/* Header Strip */}
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div>
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[#480870]">campaign</span>
                <h1 className="font-serif text-2xl font-bold tracking-tight text-[#1e1b18] sm:text-3xl">
                  Real-Time Corrigendum Radar
                </h1>
              </div>
              <p className="mt-1 text-sm text-[#735368]">
                Continuous monitoring of tender amendments, BOQ revisions, date extensions, and eligibility relaxations across GeM & CPPP.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full neu-flat-sm bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800">
                <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500"></span>
                Webhook Radar Active (Every 15s)
              </span>

              <button
                type="button"
                className="flex items-center gap-2 rounded-xl neu-button-primary px-4 py-2.5 text-xs font-semibold cursor-pointer"
              >
                <span className="material-symbols-outlined text-sm">refresh</span>
                Force Sync Portals
              </button>
            </div>
          </div>

          {/* Metric Overview Strip */}
          <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl neu-flat p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant">Amendments (7 Days)</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg neu-flat-sm bg-secondary-fixed text-on-secondary-fixed">
                  <span className="material-symbols-outlined text-base">breaking_news_alt_1</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-primary">12 Detected</p>
              <p className="mt-1 text-xs text-emerald-700 flex items-center gap-1 font-medium">
                <span className="material-symbols-outlined text-xs">done_all</span>
                All cross-referenced with your bid pipeline
              </p>
            </div>

            <div className="rounded-2xl neu-flat p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-red-800">Critical BOQ/Date Shifts</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg neu-flat-sm bg-red-100 text-red-700">
                  <span className="material-symbols-outlined text-base">priority_high</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-red-900">3 High Impact</p>
              <p className="mt-1 text-xs text-red-700">Requires re-audit of bid documents</p>
            </div>

            <div className="rounded-2xl neu-flat p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant">Deadlines Extended</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg neu-flat-sm bg-indigo-100 text-indigo-700">
                  <span className="material-symbols-outlined text-base">more_time</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-primary">+5 Days Avg</p>
              <p className="mt-1 text-xs text-on-surface-variant">CPWD & DMRC deadlines widened</p>
            </div>

            <div className="rounded-2xl neu-flat p-5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant">Monitored Tenders</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg neu-flat-sm bg-secondary-fixed text-on-secondary-fixed">
                  <span className="material-symbols-outlined text-base">radar</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-primary">24 Active</p>
              <p className="mt-1 text-xs text-on-surface-variant">Across GeM, CPPP, IREPS & DMRC</p>
            </div>
          </div>

          {/* Filters & Search Bar */}
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              {filterOptions.map((opt) => (
                <button
                  key={opt}
                  type="button"
                  onClick={() => setSelectedFilter(opt)}
                  className={`rounded-full px-4 py-1.5 text-xs font-semibold transition ${
                    selectedFilter === opt
                      ? "bg-[#480870] text-white shadow-xs"
                      : "border border-[#E9DFE4] bg-white text-[#735368] hover:bg-[#F3EBF0] hover:text-[#1e1b18]"
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>

            <div className="relative w-full sm:w-72">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[#735368]">
                search
              </span>
              <input
                type="text"
                placeholder="Search corrigendum, tender, ref..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-xl border border-[#E9DFE4] bg-white py-2 pl-9 pr-4 text-xs font-medium text-[#1e1b18] placeholder-[#735368] outline-none transition focus:border-[#480870] focus:ring-1 focus:ring-[#480870]"
              />
            </div>
          </div>

          {/* Corrigendum Feed Cards with Diff View */}
          <div className="space-y-4">
            {filteredItems.map((item) => {
              const isReviewed = reviewedItems[item.id];
              return (
                <div
                  key={item.id}
                  className={`rounded-2xl border p-6 transition ${
                    isReviewed
                      ? "border-[#E9DFE4] bg-white/70 opacity-75"
                      : item.severity === "Critical"
                      ? "border-red-200 bg-white shadow-xs"
                      : "border-[#E9DFE4] bg-white shadow-xs"
                  }`}
                >
                  {/* Top Bar of the Card */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#E9DFE4] pb-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wider ${
                          item.severity === "Critical"
                            ? "bg-red-100 text-red-800"
                            : item.severity === "Important"
                            ? "bg-amber-100 text-amber-800"
                            : "bg-[#EAE0EB] text-[#480870]"
                        }`}
                      >
                        {item.corrigendumNo}
                      </span>

                      <span className="rounded-md border border-[#E9DFE4] bg-[#F8F2F6] px-2 py-0.5 text-[11px] font-medium text-[#735368]">
                        {item.changeType}
                      </span>

                      <span className="text-xs text-[#735368]">• Published {item.publishedAt}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-[#735368]">Your Bid:</span>
                      <span className="rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700">
                        {item.bidStatus}
                      </span>
                    </div>
                  </div>

                  {/* Body Content */}
                  <div className="mt-4">
                    <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-baseline">
                      <h2 className="text-base font-bold text-[#1e1b18]">{item.tenderTitle}</h2>
                      <span className="font-mono text-xs text-[#735368]">{item.tenderRef}</span>
                    </div>
                    <p className="mt-0.5 text-xs text-[#735368]">{item.dept}</p>

                    <p className="mt-3 text-sm font-medium text-[#1e1b18]">{item.impactSummary}</p>

                    {/* Diff Inspection Box */}
                    <div className="mt-4 overflow-hidden rounded-xl border border-[#E9DFE4] bg-[#FAF5F8] text-xs">
                      <div className="grid grid-cols-1 divide-y divide-[#E9DFE4] md:grid-cols-2 md:divide-x md:divide-y-0">
                        {/* Before */}
                        <div className="p-4 bg-red-50/40">
                          <p className="text-[11px] font-bold uppercase tracking-wider text-red-800 flex items-center gap-1">
                            <span className="material-symbols-outlined text-sm">remove_circle</span>
                            Previous Specification / Requirement
                          </p>
                          <p className="mt-2 text-xs text-red-950 font-mono line-through opacity-80">
                            {item.before}
                          </p>
                        </div>

                        {/* After */}
                        <div className="p-4 bg-emerald-50/40">
                          <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1">
                            <span className="material-symbols-outlined text-sm">check_circle</span>
                            Revised Tender Term (Active Rule)
                          </p>
                          <p className="mt-2 text-xs text-emerald-950 font-mono font-semibold">
                            {item.after}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Bottom Action Footer */}
                  <div className="mt-5 flex flex-wrap items-center justify-between gap-3 pt-2">
                    <div className="flex items-center gap-2">
                      {item.reAuditRecommended && (
                        <Link
                          href="/audit"
                          className="flex items-center gap-1.5 rounded-lg bg-[#480870] px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-[#3B0066]"
                        >
                          <span className="material-symbols-outlined text-sm">auto_fix_high</span>
                          Re-Audit Bid Compliance
                        </Link>
                      )}

                      <button
                        type="button"
                        className="flex items-center gap-1 rounded-lg border border-[#E9DFE4] bg-white px-3 py-1.5 text-xs font-semibold text-[#1e1b18] hover:bg-[#F3EBF0]"
                      >
                        <span className="material-symbols-outlined text-sm text-[#480870]">picture_as_pdf</span>
                        Download Official Gazette PDF
                      </button>
                    </div>

                    <button
                      type="button"
                      onClick={() => toggleReview(item.id)}
                      className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
                        isReviewed
                          ? "border-emerald-300 bg-emerald-50 text-emerald-800"
                          : "border-[#E9DFE4] bg-white text-[#735368] hover:bg-[#F3EBF0] hover:text-[#1e1b18]"
                      }`}
                    >
                      <span className="material-symbols-outlined text-sm">
                        {isReviewed ? "check_circle" : "check"}
                      </span>
                      {isReviewed ? "Acknowledged" : "Mark as Reviewed"}
                    </button>
                  </div>
                </div>
              );
            })}

            {filteredItems.length === 0 && (
              <div className="rounded-2xl border border-[#E9DFE4] bg-white p-12 text-center text-sm text-[#735368]">
                No corrigenda found matching your filter criteria.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  </div>
  );
}
