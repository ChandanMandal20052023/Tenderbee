"use client";

import React, { useState } from "react";
import Sidebar from "@/components/Sidebar";
import DashboardHeader from "@/components/DashboardHeader";

interface VaultDoc {
  id: string;
  title: string;
  category: "Financial" | "Statutory" | "Technical" | "Certifications" | "DSC";
  refNo: string;
  validUntil: string;
  status: "Verified" | "Expiring Soon" | "Missing Sign" | "Under Audit";
  udinStatus?: string;
  fileSize: string;
  format: "PDF" | "P7S" | "ZIP";
  lastUsedIn: string;
}

export default function DocumentVaultPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);

  const documents: VaultDoc[] = [
    {
      id: "doc-1",
      title: "Audited Financial Statements & Balance Sheet (FY 2023-24)",
      category: "Financial",
      refNo: "CA/2024/UDIN-981244",
      validUntil: "31 Oct 2025",
      status: "Verified",
      udinStatus: "UDIN Verified by ICAI: 24089124AAAAAB8912",
      fileSize: "8.4 MB",
      format: "PDF",
      lastUsedIn: "CPWD/NZ/EE(E)/2024/718",
    },
    {
      id: "doc-2",
      title: "Audited Financial Statements (FY 2022-23)",
      category: "Financial",
      refNo: "CA/2023/UDIN-551029",
      validUntil: "Permanent Record",
      status: "Verified",
      udinStatus: "UDIN Verified by ICAI: 23089124AAAAAB1104",
      fileSize: "7.1 MB",
      format: "PDF",
      lastUsedIn: "IREPS/NR/HK-2024-99",
    },
    {
      id: "doc-3",
      title: "Audited Financial Statements (FY 2021-22)",
      category: "Financial",
      refNo: "CA/2022/UDIN-332190",
      validUntil: "Permanent Record",
      status: "Verified",
      udinStatus: "UDIN Verified by ICAI: 22089124AAAAAB6673",
      fileSize: "6.9 MB",
      format: "PDF",
      lastUsedIn: "AIIMS/FAC/2024/41",
    },
    {
      id: "doc-4",
      title: "Bank Solvency Certificate (₹1.50 Crore Scheduled Bank)",
      category: "Financial",
      refNo: "HDFC/SOLV/2024/0991",
      validUntil: "30 Mar 2025",
      status: "Verified",
      udinStatus: "Bank Branch Verified & Digitally Signed",
      fileSize: "1.2 MB",
      format: "PDF",
      lastUsedIn: "CPWD/NZ/EE(E)/2024/718",
    },
    {
      id: "doc-5",
      title: "UDYAM Registration Certificate (Class 1 MSE)",
      category: "Statutory",
      refNo: "UDYAM-DL-08-0098412",
      validUntil: "Permanent Registration",
      status: "Verified",
      udinStatus: "MSME Portal Live API Validated",
      fileSize: "1.8 MB",
      format: "PDF",
      lastUsedIn: "IREPS/NR/HK-2024-99",
    },
    {
      id: "doc-6",
      title: "GSTIN 3B Filings (Consolidated Last 6 Months)",
      category: "Statutory",
      refNo: "GST-07AABCT8812K1Z9",
      validUntil: "Active Filings (Sep 2024)",
      status: "Verified",
      udinStatus: "GSTN Portal API Auto-Crossmatched",
      fileSize: "4.3 MB",
      format: "PDF",
      lastUsedIn: "CPWD/NZ/EE(E)/2024/718",
    },
    {
      id: "doc-7",
      title: "EPFO & ESIC Electronic Challan Cum Returns (ECR)",
      category: "Statutory",
      refNo: "EPFO-DL/CPM/1098412",
      validUntil: "Valid for Current Fiscal Quarter",
      status: "Verified",
      udinStatus: "EPFO Portal Verified (184 Active Employees)",
      fileSize: "3.5 MB",
      format: "PDF",
      lastUsedIn: "CPWD/NZ/EE(E)/2024/718",
    },
    {
      id: "doc-8",
      title: "Similar Past Work Completion: DMRC Corporate Towers",
      category: "Technical",
      refNo: "DMRC/HK/COMP/2023/18",
      validUntil: "Permanent Credential",
      status: "Verified",
      udinStatus: "Client Certified (Value: ₹2.40 Cr)",
      fileSize: "5.1 MB",
      format: "PDF",
      lastUsedIn: "CPWD/NZ/EE(E)/2024/718",
    },
    {
      id: "doc-9",
      title: "Similar Past Work Completion: Rail Bhavan Mechanized Services",
      category: "Technical",
      refNo: "NR/HQ/FAC-2022/902",
      validUntil: "Permanent Credential",
      status: "Verified",
      udinStatus: "Client Certified (Value: ₹1.85 Cr)",
      fileSize: "4.8 MB",
      format: "PDF",
      lastUsedIn: "IREPS/NR/HK-2024-99",
    },
    {
      id: "doc-10",
      title: "ISO 45001:2018 (Occupational Health & Safety)",
      category: "Certifications",
      refNo: "CERT-OHSMS-2021-998",
      validUntil: "22 Nov 2024 (28 days left)",
      status: "Expiring Soon",
      udinStatus: "NABCB Accredited Body Check",
      fileSize: "2.1 MB",
      format: "PDF",
      lastUsedIn: "AIIMS/FAC/2024/41",
    },
    {
      id: "doc-11",
      title: "ISO 9001:2015 Quality Management System",
      category: "Certifications",
      refNo: "CERT-QMS-2023-412",
      validUntil: "15 Aug 2026",
      status: "Verified",
      udinStatus: "Accredited Body Verified",
      fileSize: "2.2 MB",
      format: "PDF",
      lastUsedIn: "CPWD/NZ/EE(E)/2024/718",
    },
    {
      id: "doc-12",
      title: "Class-3 Digital Signature Certificate (DSC) - Director Signing",
      category: "DSC",
      refNo: "eMudhra/CCA/CLASS3-ORG",
      validUntil: "14 Jun 2025",
      status: "Verified",
      udinStatus: "CCA Root Authority Validated Token",
      fileSize: "48 KB",
      format: "P7S",
      lastUsedIn: "GeM Portal Authentication",
    },
  ];

  const categories = ["All", "Financial", "Statutory", "Technical", "Certifications", "DSC"];

  const filteredDocs = documents.filter((doc) => {
    const matchesCategory = selectedCategory === "All" || doc.category === selectedCategory;
    const matchesQuery =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.refNo.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (doc.udinStatus && doc.udinStatus.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesQuery;
  });

  const handleSimulateUpload = () => {
    setIsUploading(true);
    setTimeout(() => {
      setIsUploading(false);
      setUploadSuccess(true);
      setTimeout(() => setUploadSuccess(false), 4000);
    }, 1500);
  };

  return (
    <div className="bg-surface font-sans text-on-surface antialiased min-h-screen">
      {/* Sidebar */}
      <Sidebar activeTab="vault" />

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
                <span className="material-symbols-outlined text-[#480870]">folder_special</span>
                <h1 className="font-serif text-2xl font-bold tracking-tight text-[#1e1b18] sm:text-3xl">
                  Enterprise Document Vault
                </h1>
              </div>
              <p className="mt-1 text-sm text-[#735368]">
                Centralized, cryptographically verified repository of CA certificates, UDIN credentials, and statutory filings.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleSimulateUpload}
                disabled={isUploading}
                className="flex items-center gap-2 rounded-xl bg-[#480870] px-4 py-2.5 text-xs font-semibold text-white shadow-sm transition hover:bg-[#3B0066] disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-sm">
                  {isUploading ? "progress_activity" : "upload_file"}
                </span>
                {isUploading ? "Verifying UDIN..." : "Upload & Validate Document"}
              </button>

              <button
                type="button"
                className="flex items-center gap-2 rounded-xl border border-[#E9DFE4] bg-white px-4 py-2.5 text-xs font-semibold text-[#1e1b18] shadow-sm transition hover:bg-[#F3EBF0]"
              >
                <span className="material-symbols-outlined text-sm text-[#480870]">download</span>
                Export Full Dossier
              </button>
            </div>
          </div>

          {/* Success Banner if uploaded */}
          {uploadSuccess && (
            <div className="mb-6 flex items-center justify-between rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-900 transition">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-emerald-600">verified</span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-emerald-700">Audit Successful</p>
                  <p className="text-sm font-semibold">
                    Document uploaded, OCR text indexed, and ICAI UDIN cryptographically verified!
                  </p>
                </div>
              </div>
              <span className="material-symbols-outlined cursor-pointer text-emerald-700" onClick={() => setUploadSuccess(false)}>
                close
              </span>
            </div>
          )}

          {/* Metric Overview Strip */}
          <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-[#E9DFE4] bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-[#735368]">Vault Integrity</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#EAE0EB] text-[#480870]">
                  <span className="material-symbols-outlined text-base">verified_user</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-[#1e1b18]">98.2%</p>
              <p className="mt-1 text-xs text-emerald-700 flex items-center gap-1">
                <span className="material-symbols-outlined text-xs">check_circle</span>
                18 of 19 credentials fully valid
              </p>
            </div>

            <div className="rounded-2xl border border-[#E9DFE4] bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-[#735368]">UDIN Live Match</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
                  <span className="material-symbols-outlined text-base">fact_check</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-[#1e1b18]">100% Active</p>
              <p className="mt-1 text-xs text-[#735368]">Synced with ICAI & MSME registry</p>
            </div>

            <div className="rounded-2xl border border-[#E9DFE4] bg-white p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-[#735368]">Class-3 DSC Token</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                  <span className="material-symbols-outlined text-base">token</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-[#1e1b18]">Active (Director)</p>
              <p className="mt-1 text-xs text-[#735368]">Valid through June 2025</p>
            </div>

            <div className="rounded-2xl border border-amber-200 bg-amber-50/70 p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-800">Action Required</span>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-200 text-amber-900">
                  <span className="material-symbols-outlined text-base">notification_important</span>
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold tracking-tight text-amber-900">1 Expiring</p>
              <p className="mt-1 text-xs text-amber-800">ISO 45001 due in 28 days</p>
            </div>
          </div>

          {/* Quick Drag & Drop Upload Strip */}
          <div className="mb-8 rounded-2xl border-2 border-dashed border-[#D5C2CF] bg-white/70 p-6 text-center transition hover:border-[#480870] hover:bg-white">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-[#EAE0EB] text-[#480870]">
              <span className="material-symbols-outlined text-2xl">cloud_upload</span>
            </div>
            <p className="mt-3 font-semibold text-[#1e1b18]">Drag and drop your tender compliance documents here</p>
            <p className="mt-1 text-xs text-[#735368]">
              Accepts PDF, P7S, ZIP up to 50MB. Auto-runs OCR, UDIN cross-match, and digital signature validation.
            </p>
            <div className="mt-4 flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={handleSimulateUpload}
                className="rounded-lg bg-[#480870] px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-[#3B0066]"
              >
                Browse Local Files
              </button>
              <span className="text-xs text-[#735368]">or select from Google Drive / DigiLocker</span>
            </div>
          </div>

          {/* Filters & Search Bar */}
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`rounded-full px-4 py-1.5 text-xs font-semibold transition ${
                    selectedCategory === cat
                      ? "bg-[#480870] text-white shadow-xs"
                      : "border border-[#E9DFE4] bg-white text-[#735368] hover:bg-[#F3EBF0] hover:text-[#1e1b18]"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="relative w-full sm:w-72">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[#735368]">
                search
              </span>
              <input
                type="text"
                placeholder="Search certificate, UDIN, ref..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-xl border border-[#E9DFE4] bg-white py-2 pl-9 pr-4 text-xs font-medium text-[#1e1b18] placeholder-[#735368] outline-none transition focus:border-[#480870] focus:ring-1 focus:ring-[#480870]"
              />
            </div>
          </div>

          {/* Document Table / List */}
          <div className="overflow-hidden rounded-2xl border border-[#E9DFE4] bg-white shadow-xs">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#E9DFE4] bg-[#F8F2F6] font-semibold text-[#735368]">
                    <th className="px-6 py-4">DOCUMENT / CREDENTIAL</th>
                    <th className="px-4 py-4">CATEGORY</th>
                    <th className="px-4 py-4">UDIN & INTEGRITY STATUS</th>
                    <th className="px-4 py-4">VALIDITY</th>
                    <th className="px-4 py-4">LAST ATTACHED TO</th>
                    <th className="px-6 py-4 text-right">ACTIONS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E9DFE4]">
                  {filteredDocs.map((doc) => (
                    <tr key={doc.id} className="transition hover:bg-[#FAF5F8]">
                      {/* Document Title & File Info */}
                      <td className="px-6 py-4">
                        <div className="flex items-start gap-3">
                          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#EAE0EB] text-[#480870]">
                            <span className="material-symbols-outlined text-lg">
                              {doc.format === "P7S" ? "key" : "description"}
                            </span>
                          </div>
                          <div>
                            <p className="font-semibold text-[#1e1b18]">{doc.title}</p>
                            <p className="mt-0.5 text-[11px] text-[#735368]">
                              Ref: {doc.refNo} • {doc.fileSize} • {doc.format}
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Category Badge */}
                      <td className="px-4 py-4">
                        <span className="inline-flex rounded-md border border-[#E9DFE4] bg-[#F8F2F6] px-2.5 py-1 text-[11px] font-medium text-[#735368]">
                          {doc.category}
                        </span>
                      </td>

                      {/* UDIN / Verification Status */}
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-1.5">
                          {doc.status === "Verified" ? (
                            <span className="material-symbols-outlined text-sm text-emerald-600">verified</span>
                          ) : (
                            <span className="material-symbols-outlined text-sm text-amber-600">warning</span>
                          )}
                          <span
                            className={`font-semibold ${
                              doc.status === "Verified" ? "text-emerald-700" : "text-amber-800"
                            }`}
                          >
                            {doc.status}
                          </span>
                        </div>
                        {doc.udinStatus && (
                          <p className="mt-0.5 max-w-[220px] truncate text-[11px] text-[#735368]">
                            {doc.udinStatus}
                          </p>
                        )}
                      </td>

                      {/* Validity */}
                      <td className="px-4 py-4">
                        <span
                          className={`font-medium ${
                            doc.status === "Expiring Soon" ? "font-semibold text-amber-800" : "text-[#1e1b18]"
                          }`}
                        >
                          {doc.validUntil}
                        </span>
                      </td>

                      {/* Last Attached Bid */}
                      <td className="px-4 py-4">
                        <span className="font-mono text-[11px] text-[#735368]">{doc.lastUsedIn}</span>
                      </td>

                      {/* Actions */}
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            title="Download verified document"
                            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#E9DFE4] bg-white text-[#735368] hover:bg-[#F3EBF0] hover:text-[#480870]"
                          >
                            <span className="material-symbols-outlined text-sm">download</span>
                          </button>
                          <button
                            type="button"
                            title="Re-verify against official portal"
                            className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#E9DFE4] bg-white text-[#735368] hover:bg-[#F3EBF0] hover:text-[#480870]"
                          >
                            <span className="material-symbols-outlined text-sm">sync</span>
                          </button>
                          <button
                            type="button"
                            className="rounded-lg bg-[#480870] px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-[#3B0066]"
                          >
                            Attach
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredDocs.length === 0 && (
              <div className="p-12 text-center text-sm text-[#735368]">
                No compliance documents match your search criteria.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  </div>
  );
}
