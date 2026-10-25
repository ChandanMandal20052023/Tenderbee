"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import DashboardHeader from "@/components/DashboardHeader";
import { apiClient, TenderSummary, DocumentRecord } from "@/lib/api";

interface VerificationResult {
  success: boolean;
  assessment_id?: string;
  tender_id?: string;
  overall_status?: string;
  verdicts?: Array<{
    rule_id: string;
    description: string;
    status: string;
    message?: string;
    field?: string;
    expected?: any;
    actual?: any;
    quote?: string;
    page?: number;
  }>;
  missing_documents?: Array<{
    document_type: string;
    description: string;
  }>;
  fix_list?: Array<{
    rule_id: string;
    action: string;
    severity?: string;
  }>;
  registry_verifications?: Record<string, any>;
  assessed_at?: string;
}

function OpenTendersContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("query") || searchParams.get("q") || "";

  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [selectedState, setSelectedState] = useState("All");
  const [selectedPortal, setSelectedPortal] = useState("All");
  const [tenders, setTenders] = useState<TenderSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Selected Tender for inspection & verification workflow
  const [selectedTender, setSelectedTender] = useState<TenderSummary | null>(null);
  const [tenderDetailLoading, setTenderDetailLoading] = useState(false);
  const [tenderDetails, setTenderDetails] = useState<any | null>(null);

  // Documents uploaded for this selected tender
  const [tenderDocs, setTenderDocs] = useState<DocumentRecord[]>([]);
  const [docsLoading, setDocsLoading] = useState(false);

  // Document upload state
  const [uploadDocType, setUploadDocType] = useState("ca_turnover_certificate");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccessMsg, setUploadSuccessMsg] = useState("");
  const [uploadErrorMsg, setUploadErrorMsg] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Rule engine assessment state
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<VerificationResult | null>(null);
  const [evaluationError, setEvaluationError] = useState("");

  const executeSearch = async (queryText = searchQuery) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.tenders.search({
        query: queryText.trim() || undefined,
        state: selectedState !== "All" ? selectedState : undefined,
      });

      if (res && Array.isArray(res.results)) {
        setTenders(res.results);
      } else {
        setTenders([]);
      }
    } catch (err: any) {
      setError(err.message || "Failed to query procurement search engine.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const qParam = searchParams.get("query") || searchParams.get("q");
    if (qParam) {
      setSearchQuery(qParam);
      executeSearch(qParam);
    } else {
      executeSearch("");
    }
  }, [searchParams.get("query"), searchParams.get("q"), selectedState]);

  // If tender_id is provided in URL, auto-select it for inspection & verification
  useEffect(() => {
    const targetId = searchParams.get("tender_id");
    if (targetId && tenders.length > 0) {
      const match = tenders.find((t) => t.tender_id === targetId || t.tender_number === targetId);
      if (match && (!selectedTender || (selectedTender.tender_id !== match.tender_id && selectedTender.tender_number !== match.tender_number))) {
        handleSelectTender(match);
      }
    }
  }, [searchParams.get("tender_id"), tenders]);

  const handleSelectTender = async (tender: TenderSummary) => {
    setSelectedTender(tender);
    setTenderDetails(null);
    setEvaluationResult(null);
    setEvaluationError("");
    setUploadSuccessMsg("");
    setUploadErrorMsg("");

    const targetId = tender.tender_id || tender.tender_number;

    // 1. Fetch detailed tender clauses, skimmed specs & rules
    setTenderDetailLoading(true);
    try {
      const detailed = await apiClient.tenders.get(targetId, "detailed");
      setTenderDetails(detailed);
      if (detailed) {
        setSelectedTender((prev) => (prev ? { ...prev, ...detailed } : detailed));
      }
    } catch (err) {
      console.warn("Could not load deep details:", err);
    } finally {
      setTenderDetailLoading(false);
    }

    // 2. Fetch documents already associated with this tender
    loadTenderDocs(tender.tender_id);
  };

  const loadTenderDocs = async (tId?: string) => {
    if (!tId) return;
    setDocsLoading(true);
    try {
      const res = await apiClient.documents.list(tId);
      const items = Array.isArray(res) ? res : res.results || [];
      setTenderDocs(items);
    } catch {
      setTenderDocs([]);
    } finally {
      setDocsLoading(false);
    }
  };

  const handleUploadComplianceDoc = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !selectedTender) return;

    setIsUploading(true);
    setUploadSuccessMsg("");
    setUploadErrorMsg("");

    try {
      const tenderId = selectedTender.tender_id || selectedTender.tender_number;
      const res = await apiClient.documents.upload(file, uploadDocType, tenderId);

      if (res && (res.success || res.document)) {
        setUploadSuccessMsg(`Successfully uploaded and cryptographically hashed ${file.name}`);
        loadTenderDocs(selectedTender.tender_id);
      } else {
        setUploadErrorMsg("Upload completed with warnings.");
      }
    } catch (err: any) {
      setUploadErrorMsg(err.message || "Failed to upload compliance document.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleRunRuleEngine = async () => {
    if (!selectedTender) return;
    setIsEvaluating(true);
    setEvaluationError("");
    setEvaluationResult(null);

    const tenderId = selectedTender.tender_id || selectedTender.tender_number;

    try {
      const res = await apiClient.verify.evaluate(tenderId);
      setEvaluationResult(res as any);
    } catch (err: any) {
      setEvaluationError(err.message || "Evaluation pipeline encountered an issue.");
    } finally {
      setIsEvaluating(false);
    }
  };

  const formatCurrency = (val?: number) => {
    if (!val) return "Not Disclosed";
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} Lakh`;
    return `₹${val.toLocaleString("en-IN")}`;
  };

  const filteredTenders = tenders.filter((t) => {
    if (selectedPortal === "All") return true;
    const p = (t.portal || "").toLowerCase();
    if (selectedPortal === "GeM") return p.includes("gem");
    if (selectedPortal === "CPPP") return p.includes("cppp") || p.includes("eprocure");
    if (selectedPortal === "Bihar") return p.includes("bihar") || p.includes("eproc2");
    if (selectedPortal === "IREPS") return p.includes("ireps") || p.includes("rail");
    return true;
  });

  return (
    <div className="bg-surface font-sans text-on-surface antialiased min-h-screen">
      <Sidebar activeTab="tenders" />

      <div className="lg:pl-72 flex flex-col min-h-screen">
        <DashboardHeader />

        <main className="w-full pt-16 bg-surface min-h-screen">
          <div className="flex flex-col w-full max-w-[1500px] mx-auto px-4 sm:px-8 xl:px-12 py-8">
            
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
              <div>
                <span className="text-[10px] text-on-surface-variant uppercase tracking-widest font-semibold block">
                  Procurement Discovery Engine
                </span>
                <h1 className="font-serif text-2xl sm:text-3xl font-bold text-primary mt-1">
                  Find Tenders &amp; Verify Compliance
                </h1>
                <p className="text-xs text-on-surface-variant mt-1">
                  Search live portals (GeM, CPPP, State Portals), inspect official criteria, attach compliance proofs, and execute deterministic verification.
                </p>
              </div>

              {/* Status / Quick Stats */}
              <div className="flex items-center gap-3">
                <div className="px-4 py-2 rounded-xl neu-flat bg-surface-container-lowest text-xs flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="font-semibold text-slate-700">{tenders.length} Tenders Indexed</span>
                </div>
              </div>
            </div>

            {/* Search & Filter Toolbar */}
            <div className="bg-surface-container-lowest neu-flat rounded-2xl p-5 mb-8 flex flex-col gap-4">
              <div className="flex flex-col md:flex-row items-center gap-3">
                <div className="relative flex-1 w-full">
                  <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant text-lg">
                    search
                  </span>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && executeSearch()}
                    placeholder="Search keywords, state, or tender ref (e.g. 'Sanitation in Bihar', 'Security Gaya', 'Bridge Danapur', 'OBHS')..."
                    className="w-full pl-10 pr-4 py-3 rounded-xl neu-pressed bg-[#edf1f7] text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-secondary/50 font-medium"
                  />
                </div>

                <div className="flex items-center gap-2 w-full md:w-auto">
                  <select
                    value={selectedState}
                    onChange={(e) => setSelectedState(e.target.value)}
                    aria-label="Filter by state"
                    className="px-3 py-3 rounded-xl neu-flat text-xs font-semibold text-slate-700 bg-surface-container-low focus:outline-none cursor-pointer"
                  >
                    <option value="All">All States</option>
                    <option value="Bihar">Bihar</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Maharashtra">Maharashtra</option>
                    <option value="Uttar Pradesh">Uttar Pradesh</option>
                    <option value="Rajasthan">Rajasthan</option>
                  </select>

                  <button
                    onClick={() => executeSearch()}
                    disabled={loading}
                    className="px-6 py-3 rounded-xl neu-button text-xs font-bold text-white bg-gradient-to-r from-secondary to-brand-purple flex items-center justify-center gap-2 shrink-0 cursor-pointer shadow-md hover:opacity-95"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                        </svg>
                        <span>Scanning...</span>
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined text-base">travel_explore</span>
                        <span>Discover Tenders</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Portal Pill Filters & Quick Queries */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-200/60">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[11px] font-semibold text-slate-500 mr-1">Portal:</span>
                  {["All", "GeM", "CPPP", "Bihar", "IREPS"].map((portal) => (
                    <button
                      key={portal}
                      onClick={() => setSelectedPortal(portal)}
                      className={`px-3 py-1 rounded-full text-xs font-semibold transition-all cursor-pointer ${
                        selectedPortal === portal
                          ? "neu-pressed bg-secondary text-white shadow-sm"
                          : "neu-flat text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      {portal}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[11px] font-semibold text-slate-500">Quick Picks:</span>
                  {[
                    "Sanitation Bihar",
                    "Security Sub-stations Gaya",
                    "Road Overbridge Danapur",
                    "Medical Diagnostic Kits",
                    "Western Railway Coaches Cleaning",
                  ].map((preset) => (
                    <button
                      key={preset}
                      onClick={() => {
                        setSearchQuery(preset);
                        executeSearch(preset);
                      }}
                      className="text-[11px] px-2.5 py-0.5 rounded-md neu-flat text-slate-600 hover:text-secondary hover:underline cursor-pointer"
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {error && (
              <div className="mb-6 p-4 rounded-xl neu-inset border border-rose-200 bg-rose-50/60 text-rose-700 text-xs flex items-center gap-2">
                <span className="material-symbols-outlined text-base">error</span>
                <span>{error}</span>
              </div>
            )}

            {/* Main Content Grid: Tenders List */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredTenders.map((tender, idx) => {
                const isSelected = selectedTender?.tender_id === tender.tender_id || selectedTender?.tender_number === tender.tender_number;
                const tenderKey = tender.tender_id || (tender as any).id || tender.tender_number || (tender as any).external_id || `tender-${idx}`;
                return (
                  <div
                    key={tenderKey}
                    className={`bg-surface-container-lowest neu-flat rounded-2xl p-6 flex flex-col justify-between transition-all border ${
                      isSelected
                        ? "border-secondary ring-2 ring-secondary/20 shadow-lg -translate-y-1"
                        : "border-transparent hover:-translate-y-0.5"
                    }`}
                  >
                    <div>
                      {/* Top Badges */}
                      <div className="flex items-center justify-between gap-2 mb-3">
                        <div className="flex items-center gap-1.5 flex-wrap min-w-0">
                          <span className="text-[11px] px-2.5 py-0.5 rounded-full neu-pressed-sm text-primary font-mono font-bold truncate max-w-[200px] border border-secondary/20 bg-surface-container-lowest">
                            {tender.tender_number}
                          </span>
                          {tender.state && (
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-surface-container text-slate-600 font-semibold">
                              {tender.state}
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider bg-secondary-fixed text-on-secondary-fixed shrink-0">
                          {tender.portal || "eProcurement"}
                        </span>
                      </div>

                      {/* Title */}
                      <h2 className="font-serif text-base font-bold text-primary line-clamp-2 mb-1.5 leading-snug">
                        {tender.title}
                      </h2>

                      {/* Buyer & Dealing Officer */}
                      <div className="flex flex-col gap-0.5 mb-3 text-xs text-on-surface-variant">
                        <p className="line-clamp-1 flex items-center gap-1.5 font-medium">
                          <span className="material-symbols-outlined text-sm text-slate-400">account_balance</span>
                          <span>{tender.buyer_name || "Procurement Authority"}</span>
                        </p>
                        {tender.dealing_officer && (
                          <p className="line-clamp-1 text-[11px] text-slate-500 flex items-center gap-1.5 pl-0.5">
                            <span className="material-symbols-outlined text-xs text-slate-400">badge</span>
                            <span>Officer: {tender.dealing_officer}</span>
                          </p>
                        )}
                      </div>

                      {/* Key Skimmed Financials & Specs */}
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 p-3 rounded-xl neu-inset bg-[#edf1f7] mb-4 text-xs">
                        <div>
                          <span className="text-[10px] uppercase font-semibold text-slate-500 block">Est. Value</span>
                          <span className="font-bold text-emerald-800">{formatCurrency(tender.estimated_value_inr)}</span>
                        </div>
                        <div>
                          <span className="text-[10px] uppercase font-semibold text-slate-500 block">EMD Deposit</span>
                          <span className="font-semibold text-slate-800">{formatCurrency(tender.emd_amount_inr)}</span>
                        </div>
                        <div>
                          <span className="text-[10px] uppercase font-semibold text-slate-500 block">Tender Fee</span>
                          <span className="font-semibold text-slate-800">
                            {tender.tender_fee_inr ? formatCurrency(tender.tender_fee_inr) : "Exempt / Free"}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] uppercase font-semibold text-slate-500 block">Duration</span>
                          <span className="font-semibold text-slate-700">{tender.tenure_months || 12} Months</span>
                        </div>
                        <div>
                          <span className="text-[10px] uppercase font-semibold text-slate-500 block">Deadline</span>
                          <span className="font-semibold text-slate-700 truncate block">
                            {tender.submission_deadline ? new Date(tender.submission_deadline).toLocaleDateString("en-IN") : "Active"}
                          </span>
                        </div>
                        <div>
                          <span className="text-[10px] uppercase font-semibold text-slate-500 block">Checklist</span>
                          <span className="font-semibold text-primary truncate block">
                            {tender.mandatory_documents?.length ? `${tender.mandatory_documents.length} Proofs` : "Criteria Ready"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Action Button */}
                    <button
                      onClick={() => handleSelectTender(tender)}
                      className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                        isSelected
                          ? "bg-secondary text-white shadow-md"
                          : "neu-button text-slate-800 hover:text-secondary"
                      }`}
                    >
                      <span className="material-symbols-outlined text-sm">fact_check</span>
                      <span>{isSelected ? "Selected for Verification" : "Select & Verify Compliance"}</span>
                    </button>
                  </div>
                );
              })}
            </div>

            {filteredTenders.length === 0 && !loading && (
              <div className="p-12 text-center neu-flat rounded-3xl bg-surface-container-lowest my-8">
                <span className="material-symbols-outlined text-4xl text-slate-400 mb-2">find_in_page</span>
                <h3 className="font-serif text-lg font-bold text-slate-700">No tenders matched your search</h3>
                <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                  Try adjusting your query, clearing state filters, or selecting one of the quick picks above.
                </p>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Selected Tender Modal / Drawer (The Interactive Compliance Workflow) */}
      {selectedTender && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#edf1f7] neu-flat rounded-3xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden shadow-2xl border border-white/50">
            
            {/* Modal Header */}
            <div className="px-6 py-5 border-b border-slate-200/80 flex items-start justify-between gap-4 bg-surface-container-lowest">
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full neu-pressed-sm text-slate-700 font-mono font-bold">
                    {selectedTender.tender_number}
                  </span>
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider bg-secondary-fixed text-on-secondary-fixed">
                    {selectedTender.portal || "Portal"}
                  </span>
                  <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-semibold">
                    Live Verified
                  </span>
                </div>
                <h2 className="font-serif text-xl font-bold text-primary leading-tight">
                  {selectedTender.title}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {selectedTender.buyer_name} • Est. Value: {formatCurrency(selectedTender.estimated_value_inr)}
                </p>
              </div>

              <button
                onClick={() => setSelectedTender(null)}
                className="w-8 h-8 rounded-full neu-flat flex items-center justify-center text-slate-500 hover:text-slate-900 cursor-pointer"
              >
                <span className="material-symbols-outlined text-lg">close</span>
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-800 text-sm">
              
              {/* Step 1: Official Skimmed Tender Specifications from Backend Engine */}
              <div className="p-5 rounded-2xl neu-inset bg-[#e8ecf4] space-y-4">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <h4 className="font-bold text-xs uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-base text-secondary">fact_check</span>
                    <span>1. Official Tender Specifications &amp; Skimmed Notice Data</span>
                  </h4>
                  <div className="flex items-center gap-2">
                    {selectedTender.source_url && (
                      <a
                        href={selectedTender.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[11px] font-semibold text-primary hover:underline flex items-center gap-1 neu-flat-sm px-2.5 py-1 rounded-md bg-white/80"
                      >
                        <span>Official Portal Notice</span>
                        <span className="material-symbols-outlined text-xs">open_in_new</span>
                      </a>
                    )}
                    {selectedTender.content_hash && (
                      <span className="text-[10px] font-mono text-slate-500 bg-white/60 px-2 py-0.5 rounded border border-slate-200">
                        SHA-256: {selectedTender.content_hash.slice(0, 10)}...
                      </span>
                    )}
                  </div>
                </div>

                {tenderDetailLoading ? (
                  <div className="p-4 bg-white/70 rounded-xl flex items-center gap-2 text-xs text-slate-500 italic">
                    <span className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin"></span>
                    <span>Ingesting skimmed parameters, fees &amp; mandatory checklists from backend...</span>
                  </div>
                ) : (
                  <>
                    {/* Organization Hierarchy & Dealing Officer */}
                    <div className="p-3.5 bg-white/80 rounded-xl border border-white/60 space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div>
                          <span className="text-[10px] uppercase font-bold text-slate-500 block">Issuing Authority / Division</span>
                          <span className="text-xs font-bold text-slate-800">{selectedTender.buyer_name}</span>
                        </div>
                        {selectedTender.dealing_officer && (
                          <div className="sm:text-right">
                            <span className="text-[10px] uppercase font-bold text-slate-500 block">Inviting / Dealing Officer</span>
                            <span className="text-xs font-semibold text-secondary">{selectedTender.dealing_officer}</span>
                          </div>
                        )}
                      </div>
                      
                      {selectedTender.org_hierarchy && selectedTender.org_hierarchy.length > 0 && (
                        <div className="pt-2 border-t border-slate-100 flex items-center gap-1.5 flex-wrap text-[11px] text-slate-600">
                          <span className="font-semibold text-slate-400">Hierarchy:</span>
                          {selectedTender.org_hierarchy.map((lvl, idx) => (
                            <React.Fragment key={idx}>
                              <span className="font-medium bg-slate-100 px-2 py-0.5 rounded">{lvl}</span>
                              {idx < (selectedTender.org_hierarchy?.length || 0) - 1 && (
                                <span className="text-slate-400">&gt;</span>
                              )}
                            </React.Fragment>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Financial Terms & Fees Matrix */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">Advertised Value</span>
                        <span className="font-bold text-emerald-800 text-sm">
                          {formatCurrency(selectedTender.estimated_value_inr)}
                        </span>
                      </div>
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">EMD Deposit</span>
                        <span className="font-bold text-slate-800 text-sm">
                          {formatCurrency(selectedTender.emd_amount_inr)}
                        </span>
                      </div>
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">Tender Notice Fee</span>
                        <span className="font-semibold text-slate-800">
                          {selectedTender.tender_fee_inr ? formatCurrency(selectedTender.tender_fee_inr) : "Exempt / Free"}
                        </span>
                      </div>
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">Processing Fee</span>
                        <span className="font-semibold text-slate-800">
                          {selectedTender.processing_fee_inr ? formatCurrency(selectedTender.processing_fee_inr) : "Nil"}
                        </span>
                      </div>
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">Contract Duration</span>
                        <span className="font-semibold text-slate-800">
                          {selectedTender.tenure_months ? `${selectedTender.tenure_months} Months` : "12 Months"}
                        </span>
                      </div>
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">Submission Deadline</span>
                        <span className="font-semibold text-slate-800">
                          {selectedTender.submission_deadline ? new Date(selectedTender.submission_deadline).toLocaleString("en-IN") : "Active"}
                        </span>
                      </div>
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">Min Annual Turnover</span>
                        <span className="font-semibold text-slate-800">
                          {tenderDetails?.eligibility_rules?.min_annual_turnover_inr
                            ? `₹${(tenderDetails.eligibility_rules.min_annual_turnover_inr / 100000).toFixed(2)} Lakh`
                            : "Calculated at 30% contract value"}
                        </span>
                      </div>
                      <div className="p-3 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">MSME Exemption</span>
                        <span className="font-semibold text-slate-800">
                          {selectedTender.portal?.includes("GeM") ? "Rule 153 GFR Applicable" : "Udyam Certificate Valid"}
                        </span>
                      </div>
                    </div>

                    {/* Official Mandatory Documents Checklist */}
                    {selectedTender.mandatory_documents && selectedTender.mandatory_documents.length > 0 && (
                      <div className="p-3.5 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block mb-2">
                          Mandatory Compliance Documents Specified by Tender Notice ({selectedTender.mandatory_documents.length})
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {selectedTender.mandatory_documents.map((docName, idx) => {
                            const isUploaded = tenderDocs.some(
                              (d) =>
                                d.document_type?.toLowerCase().includes(docName.toLowerCase().replace(/[^a-z0-9]/g, "")) ||
                                d.file_name?.toLowerCase().includes(docName.toLowerCase().slice(0, 4))
                            );
                            return (
                              <div
                                key={idx}
                                className={`text-[11px] px-2.5 py-1 rounded-lg flex items-center gap-1.5 border ${
                                  isUploaded
                                    ? "bg-emerald-50 border-emerald-300 text-emerald-800 font-bold"
                                    : "bg-surface-container-lowest border-slate-200 text-slate-700 font-medium"
                                }`}
                              >
                                <span className="material-symbols-outlined text-xs">
                                  {isUploaded ? "check_circle" : "pending"}
                                </span>
                                <span>{docName}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Official Attached Notice Documents (NIT, BOQ) */}
                    {selectedTender.attachments && selectedTender.attachments.length > 0 && (
                      <div className="p-3.5 bg-white/80 rounded-xl border border-white/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block mb-2">
                          Official Tender Notices &amp; Schedules ({selectedTender.attachments.length} files)
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {selectedTender.attachments.map((att, idx) => (
                            <div
                              key={idx}
                              className="p-2.5 rounded-lg bg-surface-container-lowest border border-slate-200 flex items-center justify-between text-xs"
                            >
                              <div className="flex items-center gap-2 min-w-0">
                                <span className="material-symbols-outlined text-base text-rose-500 shrink-0">description</span>
                                <div className="min-w-0">
                                  <span className="font-semibold text-slate-800 truncate block">
                                    {att.file_name || `Document_${idx + 1}`}
                                  </span>
                                  {att.file_size_bytes && (
                                    <span className="text-[10px] text-slate-400">
                                      {(att.file_size_bytes / 1024).toFixed(1)} KB
                                    </span>
                                  )}
                                </div>
                              </div>
                              <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">
                                Attached NIT
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>

              {/* Step 2: Upload Compliance Document against this selected tender */}
              <div className="p-5 rounded-2xl neu-flat bg-surface-container-lowest">
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div>
                    <h4 className="font-bold text-sm text-slate-800 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-base text-secondary">upload_file</span>
                      <span>2. Upload Compliance Document Against This Tender</span>
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Upload your organization’s PDF proofs (CA Turnover Certificate, Udyam MSME, GST, Work Exp) to evaluate.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                      Document Category *
                    </label>
                    <select
                      value={uploadDocType}
                      onChange={(e) => setUploadDocType(e.target.value)}
                      aria-label="Select document category"
                      className="w-full px-3 py-2.5 rounded-xl neu-inset bg-[#edf1f7] text-xs font-medium text-slate-800 focus:outline-none"
                    >
                      <option value="ca_turnover_certificate">CA Turnover Certificate &amp; Balance Sheet</option>
                      <option value="udyam_certificate">Udyam MSME Registration</option>
                      <option value="gst_certificate">GST Registration Certificate</option>
                      <option value="pan_card">PAN Card</option>
                      <option value="work_experience_certificate">Work Experience Certificate</option>
                      <option value="banking_reference_annexure_x">Banking Reference (Annexure X)</option>
                      <option value="other">Other Compliance Proof</option>
                    </select>
                  </div>

                  <div className="md:col-span-2 flex items-center gap-2">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf"
                      onChange={handleUploadComplianceDoc}
                      className="hidden"
                      id="compliance-doc-file"
                    />
                    <label
                      htmlFor="compliance-doc-file"
                      className={`flex-1 py-2.5 px-4 rounded-xl neu-button text-xs font-bold text-slate-800 flex items-center justify-center gap-2 cursor-pointer hover:text-secondary ${
                        isUploading ? "opacity-50 pointer-events-none" : ""
                      }`}
                    >
                      {isUploading ? (
                        <>
                          <svg className="animate-spin h-4 w-4 text-secondary" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                          </svg>
                          <span>Validating &amp; Storing PDF...</span>
                        </>
                      ) : (
                        <>
                          <span className="material-symbols-outlined text-base">attach_file</span>
                          <span>Select &amp; Upload PDF Document</span>
                        </>
                      )}
                    </label>
                  </div>
                </div>

                {uploadSuccessMsg && (
                  <div className="mt-3 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    <span>{uploadSuccessMsg}</span>
                  </div>
                )}

                {uploadErrorMsg && (
                  <div className="mt-3 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">error</span>
                    <span>{uploadErrorMsg}</span>
                  </div>
                )}

                {/* Attached Documents for this Tender */}
                <div className="mt-4 pt-4 border-t border-slate-200/60">
                  <span className="text-[11px] font-semibold text-slate-500 block mb-2">
                    Attached Documents ({tenderDocs.length}):
                  </span>
                  {docsLoading ? (
                    <p className="text-xs text-slate-400">Loading documents...</p>
                  ) : tenderDocs.length > 0 ? (
                    <div className="space-y-1.5">
                      {tenderDocs.map((doc) => (
                        <div
                          key={doc.id}
                          className="p-2.5 rounded-xl bg-[#edf1f7] neu-inset flex items-center justify-between text-xs"
                        >
                          <div className="flex items-center gap-2 truncate">
                            <span className="material-symbols-outlined text-base text-secondary">description</span>
                            <span className="font-semibold text-slate-800 truncate">{doc.file_name}</span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 text-slate-600 font-mono">
                              {doc.document_type}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-500 font-mono">
                            SHA: {doc.sha256_hash?.slice(0, 8)}...
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 italic">No documents attached yet for this tender.</p>
                  )}
                </div>
              </div>

              {/* Step 3: Run Deterministic Rule Engine */}
              <div className="p-5 rounded-2xl neu-flat bg-surface-container-lowest">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                  <div>
                    <h4 className="font-bold text-sm text-slate-800 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-base text-amber-500">bolt</span>
                      <span>3. Deterministic Compliance Evaluation</span>
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Runs all 7 stages: Cryptographic signatures, turnover thresholds, MSME exemptions, and audit row writing.
                    </p>
                  </div>

                  <button
                    onClick={handleRunRuleEngine}
                    disabled={isEvaluating}
                    className="py-2.5 px-6 rounded-xl neu-button text-xs font-bold text-white bg-gradient-to-r from-secondary to-brand-purple flex items-center justify-center gap-2 cursor-pointer shadow-md hover:opacity-95 shrink-0"
                  >
                    {isEvaluating ? (
                      <>
                        <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                        </svg>
                        <span>Executing Rule Engine...</span>
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined text-base">play_arrow</span>
                        <span>Run Rule Engine Evaluation</span>
                      </>
                    )}
                  </button>
                </div>

                {evaluationError && (
                  <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">warning</span>
                    <span>{evaluationError}</span>
                  </div>
                )}

                {/* Evaluation Results Matrix */}
                {evaluationResult && (
                  <div className="mt-4 space-y-4">
                    {/* Overall Status Banner */}
                    <div
                      className={`p-4 rounded-xl flex items-center justify-between border ${
                        evaluationResult.overall_status === "READY"
                          ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                          : evaluationResult.overall_status === "ATTENTION"
                          ? "bg-amber-50 border-amber-200 text-amber-800"
                          : "bg-rose-50 border-rose-200 text-rose-800"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="material-symbols-outlined text-2xl">
                          {evaluationResult.overall_status === "READY"
                            ? "check_circle"
                            : evaluationResult.overall_status === "ATTENTION"
                            ? "warning"
                            : "cancel"}
                        </span>
                        <div>
                          <span className="text-xs font-bold uppercase tracking-wider block">
                            Overall Evaluation Verdict
                          </span>
                          <span className="font-serif text-lg font-bold">
                            {evaluationResult.overall_status === "READY"
                              ? "QUALIFIED / READY TO BID"
                              : evaluationResult.overall_status === "ATTENTION"
                              ? "CONDITIONAL / ACTION REQUIRED"
                              : "INCOMPLETE / DISQUALIFIED"}
                          </span>
                        </div>
                      </div>

                      <span className="text-xs font-mono font-semibold">
                        Assessment ID: {evaluationResult.assessment_id?.slice(0, 10)}
                      </span>
                    </div>

                    {/* Verdicts List */}
                    {evaluationResult.verdicts && evaluationResult.verdicts.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-xs font-bold text-slate-700 block">Evaluated Rule Matrix:</span>
                        {evaluationResult.verdicts.map((v, idx) => (
                          <div
                            key={idx}
                            className="p-3 rounded-xl bg-[#edf1f7] neu-inset flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <span className="font-mono font-bold text-slate-700">{v.rule_id}</span>
                                <span className="text-slate-800 font-medium">{v.description}</span>
                              </div>
                              {v.quote && (
                                <p className="text-[11px] text-slate-500 italic mt-0.5">
                                  &ldquo;{v.quote}&rdquo; {v.page ? `(Page ${v.page})` : ""}
                                </p>
                              )}
                            </div>

                            <span
                              className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shrink-0 ${
                                v.status === "READY"
                                  ? "bg-emerald-100 text-emerald-800"
                                  : v.status === "ATTENTION"
                                  ? "bg-amber-100 text-amber-800"
                                  : "bg-rose-100 text-rose-800"
                              }`}
                            >
                              {v.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Missing Documents Checklist */}
                    {evaluationResult.missing_documents && evaluationResult.missing_documents.length > 0 && (
                      <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200/80 text-xs text-amber-900">
                        <span className="font-bold block mb-1">Missing Compliance Documents:</span>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-700">
                          {evaluationResult.missing_documents.map((m, i) => (
                            <li key={i}>{m.description || m.document_type}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-slate-200/80 flex items-center justify-between bg-surface-container-lowest">
              <span className="text-xs text-slate-500">
                TenderBee Deterministic Verification &bull; Zero Hallucination Engine
              </span>
              <button
                onClick={() => setSelectedTender(null)}
                className="px-5 py-2 rounded-xl neu-button text-xs font-bold text-slate-700 cursor-pointer"
              >
                Close Window
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function OpenTendersPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-surface flex items-center justify-center">
          <div className="flex items-center gap-3 px-6 py-4 rounded-2xl neu-flat bg-white text-slate-700 text-sm font-semibold">
            <span className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin"></span>
            <span>Loading procurement tenders workspace...</span>
          </div>
        </div>
      }
    >
      <OpenTendersContent />
    </Suspense>
  );
}
