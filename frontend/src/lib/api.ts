/**
 * Centralized, typed API Client for TenderBee.
 * All frontend requests go through the same-origin Next.js server layer (/api/backend/...)
 * with automatic silent 401 refresh (1 retry) and strict generic error handling.
 */

export interface UserProfile {
  id: number;
  email: string;
  username: string;
  role: "owner" | "reviewer" | "member" | string;
  organization?: {
    id: string;
    name: string;
    gstin?: string;
    udyam_number?: string;
    pan?: string;
    created_at: string;
  } | null;
  date_joined: string;
}

export interface TenderSummary {
  tender_id: string;
  tender_number: string;
  title: string;
  buyer_name: string;
  state?: string;
  category?: string;
  estimated_value_inr?: number;
  emd_amount_inr?: number;
  tender_fee_inr?: number;
  processing_fee_inr?: number;
  tenure_months?: number;
  submission_deadline?: string;
  portal?: string;
  source_url?: string;
  status: string;
  summary?: string;
  has_pdf_document?: boolean;
  dealing_officer?: string;
  org_hierarchy?: string[];
  mandatory_documents?: string[];
  attachments?: Array<{
    label?: string;
    file_name?: string;
    file_size_bytes?: number;
    remote_path?: string;
    [key: string]: any;
  }>;
  nit_attachment?: any;
  boq_attachment?: any;
  preview_details?: Record<string, any>;
  content_hash?: string;
  fetched_at?: string;
  mode?: string;
}

export interface AsyncJobStatus {
  id: string;
  job_type: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  progress: number;
  target_id: string;
  result: Record<string, any>;
  error?: string;
}

export interface RuleItem {
  id: string;
  rule_id: string;
  rule_type: string;
  description: string;
  document_type: string;
  parameters: Record<string, any>;
  quote?: string;
  page?: number;
  is_mandatory: boolean;
  is_dismissed: boolean;
}

export interface RulePackDetail {
  id: string;
  tender_id: string;
  version: number;
  status: "DRAFT" | "FROZEN" | "ARCHIVED";
  content_hash: string;
  frozen_hash?: string;
  confirmed_by?: string;
  confirmed_at?: string;
  items: RuleItem[];
}

export interface AuditEntry {
  id: string;
  event_type: string;
  actor: string;
  target_id: string;
  payload_hash: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface DocumentRecord {
  id: string;
  file_name: string;
  document_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  is_digitally_signed: boolean;
  signature_valid: boolean;
  signature_details: Record<string, any>;
  extracted_data: Record<string, any>;
  uploaded_at: string;
}

export interface VerificationAssessmentRecord {
  id: string;
  tender: string;
  tender_external_id?: string;
  tender_title?: string;
  rule_pack: string;
  overall_status: "READY" | "NEEDS_REVIEW" | "BLOCKED";
  verdicts_data: Array<{
    rule_id: string;
    verdict: string;
    description: string;
    citations?: string[];
  }>;
  missing_documents: string[];
  fix_list: Array<{ item: string; priority: string }>;
  verdict_overrides?: Array<{
    rule_id: string;
    original_verdict: string;
    new_verdict: string;
    reason: string;
    overridden_by: string;
    timestamp: string;
  }>;
  assessed_by: string;
  assessed_at: string;
}

export interface EvidenceCitationRecord {
  id: string;
  document: string;
  document_name?: string;
  document_type?: string;
  field_key: string;
  page_number: number;
  quote: string;
  bounding_box: Record<string, any>;
  confidence: number;
  created_at: string;
}

export interface ComplianceDossierRecord {
  success: boolean;
  dossier_id: string;
  dossier_fingerprint: string;
  generated_at: string;
  generated_by: string;
  security_seal: {
    algorithm: string;
    root_authority: string;
    tamper_proof: boolean;
    cryptographic_hash: string;
  };
  envelope_status: string;
  compliance_score: number;
  organization: {
    name: string;
    gstin: string;
    udyam_number: string;
    pan: string;
    category: string;
  };
  tender: {
    id: string;
    tender_number: string;
    title: string;
    buyer_name: string;
    portal: string;
    location: string;
    estimated_value_inr: number;
    emd_amount_inr: number;
    mse_exemption: string;
    submission_deadline: string;
  };
  verdicts: Array<{
    rule_id: string;
    status: string;
    message: string;
    document_type?: string;
    clause?: string;
  }>;
  missing_documents: string[];
  fix_list: Array<{ item: string; priority: string }>;
  registry_verifications: {
    overall_registry_status: string;
    registries: Record<string, { status: string; source: string; verified: boolean }>;
  };
  attached_documents: Array<{
    id: string;
    file_name: string;
    document_type: string;
    sha256_hash: string;
    size_kb: number;
    is_digitally_signed: boolean;
  }>;
  audit_chain: Array<{
    id: string;
    event_type: string;
    actor: string;
    payload_hash: string;
    timestamp: string;
  }>;
  legal_attestation: string;
}

let isRefreshing = false;
let refreshSubscribers: Array<(tokenRefreshed: boolean) => void> = [];

function onRefreshed(success: boolean) {
  refreshSubscribers.forEach((callback) => callback(success));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback: (tokenRefreshed: boolean) => void) {
  refreshSubscribers.push(callback);
}

class APIClient {
  private basePath = "/api/backend";

  private async fetchInternal(url: string, options: RequestInit = {}, isRetry = false): Promise<Response> {
    const defaultHeaders: Record<string, string> = {
      Accept: "application/json",
    };

    if (!(options.body instanceof FormData)) {
      defaultHeaders["Content-Type"] = "application/json";
    }

    const mergedOptions: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers as Record<string, string>),
      },
      credentials: "same-origin",
    };
 
    let cleanPath = url.startsWith("/") ? url : `/${url}`;
    const queryIdx = cleanPath.indexOf("?");
    if (queryIdx !== -1) {
      const pathPart = cleanPath.slice(0, queryIdx).replace(/\/+$/, "");
      cleanPath = `${pathPart}${cleanPath.slice(queryIdx)}`;
    } else {
      cleanPath = cleanPath.replace(/\/+$/, "");
    }

    const targetUrl = url.startsWith("http") ? url : `${this.basePath}${cleanPath}`;
    const response = await fetch(targetUrl, mergedOptions);

    // If 401 Unauthorized and not already retrying or on auth endpoint -> trigger silent refresh
    const isAuthEndpoint =
      url.includes("/auth/login/") ||
      url.includes("/auth/refresh/") ||
      url.includes("/auth/register/") ||
      url.includes("/auth/me/");

    if (response.status === 401 && !isRetry && !isAuthEndpoint && typeof window !== "undefined") {
      const pathname = window.location.pathname;
      const isPublicPage = pathname === "/" || pathname.startsWith("/tenders");

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          addRefreshSubscriber(async (success) => {
            if (success) {
              try {
                const retryRes = await this.fetchInternal(url, options, true);
                resolve(retryRes);
              } catch (e) {
                reject(e);
              }
            } else {
              if (!isPublicPage) {
                window.location.href = "/login";
              }
              reject(new Error("Session expired. Please log in again."));
            }
          });
        });
      }

      isRefreshing = true;
      try {
        const refreshRes = await this.auth.refresh();
        isRefreshing = false;
        if (refreshRes && refreshRes.success) {
          onRefreshed(true);
          return this.fetchInternal(url, options, true);
        } else {
          onRefreshed(false);
          if (!isPublicPage) {
            window.location.href = "/login";
          }
          throw new Error("Authentication expired.");
        }
      } catch (err) {
        isRefreshing = false;
        onRefreshed(false);
        if (!isPublicPage) {
          window.location.href = "/login";
        }
        throw new Error("Authentication expired. Please log in.");
      }
    }

    return response;
  }

  private async request<T = any>(url: string, options: RequestInit = {}): Promise<T> {
    const response = await this.fetchInternal(url, options);
    if (!response.ok) {
      let errorMsg = `Server error (${response.status}): An error occurred while processing your request.`;
      try {
        const rawText = await response.text();
        try {
          const errJson = JSON.parse(rawText);
          errorMsg = errJson.error || errJson.message || errJson.detail || (typeof errJson === "string" ? errJson : JSON.stringify(errJson));
        } catch {
          if (rawText && rawText.length < 300) {
            errorMsg = rawText;
          } else if (rawText) {
            errorMsg = `Server returned status ${response.status} (${response.statusText})`;
          }
        }
      } catch {
        // Fallback generic message
      }
      throw new Error(errorMsg);
    }

    if (response.status === 204) {
      return {} as T;
    }
    return response.json();
  }

  // --- 1. Authentication ---
  public auth = {
    register: (data: { organization_name: string; email: string; password: string; username?: string; gstin?: string }) =>
      this.request<{ success: boolean; user: UserProfile }>("/api/v1/auth/register/", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    login: (credentials: { email: string; password: string }) =>
      this.request<{ success: boolean; user: UserProfile }>("/api/v1/auth/login/", {
        method: "POST",
        body: JSON.stringify(credentials),
      }),

    refresh: () =>
      this.request<{ success: boolean; user: UserProfile }>("/api/v1/auth/refresh/", {
        method: "POST",
        body: JSON.stringify({}),
      }),

    logout: () =>
      this.request<{ success: boolean; message: string }>("/api/v1/auth/logout/", {
        method: "POST",
        body: JSON.stringify({}),
      }),

    me: () => this.request<UserProfile>("/api/v1/auth/me/"),
  };

  // --- 2. Tenders & Discovery ---
  public tenders = {
    search: (params: { query?: string; q?: string; state?: string; category?: string; page?: number; limit?: number } = {}) => {
      const q = new URLSearchParams();
      const term = params.q || params.query;
      if (term) {
        q.set("query", term);
        q.set("q", term);
      }
      if (params.state) q.set("state", params.state);
      if (params.category) q.set("category", params.category);
      if (params.page) q.set("page", String(params.page));
      if (params.limit) q.set("limit", String(params.limit));
      return this.request<{ success: boolean; total_matches: number; results: TenderSummary[] }>(
        `/api/v1/tenders/search/?${q.toString()}`
      );
    },

    list: () => this.request<{ results?: TenderSummary[]; count?: number } | TenderSummary[]>("/api/v1/tenders/"),

    get: (identifier: string, mode: "skim" | "detailed" = "skim") =>
      this.request<TenderSummary & { extraction?: any }>(`/api/v1/tenders/${encodeURIComponent(identifier)}/?mode=${mode}`),

    intake: (data: { identifier: string; force_refresh?: boolean }) =>
      this.request<{ success: boolean; tender_id: string; rule_pack_id?: string }>("/api/v1/tenders/intake/", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    uploadPdf: (file: File, orgId?: string) => {
      const formData = new FormData();
      formData.append("pdf_file", file);
      if (orgId) formData.append("org_id", orgId);
      return this.request<{
        success: boolean;
        tender_id: string;
        tender_number: string;
        tender_title: string;
        buyer_name: string;
        submission_deadline: string;
        estimated_value_inr?: number;
        emd_amount_inr?: number;
        rule_pack_id: string;
        rule_pack: any;
        extraction: any;
      }>("/api/v1/tenders/upload-pdf/", {
        method: "POST",
        body: formData,
      });
    },
  };

  // --- 3. Rule Packs ---
  public rules = {
    list: (tenderId?: string) => {
      const q = tenderId ? `?tender_id=${encodeURIComponent(tenderId)}` : "";
      return this.request<{ results?: RulePackDetail[] } | RulePackDetail[]>(`/api/v1/rules/${q}`);
    },

    get: (id: string) => this.request<RulePackDetail>(`/api/v1/rules/${encodeURIComponent(id)}/`),

    confirm: (rulePackId: string, confirmedBy?: string) =>
      this.request<{ success: boolean; frozen_hash: string; message: string }>(
        `/api/v1/rules/${encodeURIComponent(rulePackId)}/confirm/`,
        {
          method: "POST",
          body: JSON.stringify({ confirmed_by: confirmedBy }),
        }
      ),

    updateItem: (rulePackId: string, itemId: string, patchData: Partial<RuleItem>) =>
      this.request<RuleItem>(`/api/v1/rules/${encodeURIComponent(rulePackId)}/items/${encodeURIComponent(itemId)}/`, {
        method: "PATCH",
        body: JSON.stringify(patchData),
      }),
  };

  // --- 4. Documents & Vault ---
  public documents = {
    list: (tenderId?: string) => {
      const q = tenderId ? `?tender_id=${encodeURIComponent(tenderId)}` : "";
      return this.request<{ results?: DocumentRecord[] } | DocumentRecord[]>(`/api/v1/documents/${q}`);
    },

    get: (id: string) => this.request<DocumentRecord>(`/api/v1/documents/${encodeURIComponent(id)}/`),

    upload: (file: File, documentType: string, tenderId?: string) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("document_type", documentType);
      if (tenderId) formData.append("tender_id", tenderId);

      return this.request<{ success: boolean; job_id: string; job_url: string; document: DocumentRecord }>(
        "/api/v1/documents/upload/",
        {
          method: "POST",
          body: formData,
        }
      );
    },

    downloadUrl: (id: string) => `/api/backend/api/v1/documents/${encodeURIComponent(id)}/download/`,
  };

  // --- 5. Compliance Verification ---
  public verify = {
    evaluate: (tenderId: string, rulePackId?: string) =>
      this.request<{ success: boolean; overall_status: string; assessment_id: string; fix_list: any[] }>(
        "/api/v1/verify/evaluate/",
        {
          method: "POST",
          body: JSON.stringify({ tender_id: tenderId, rule_pack_id: rulePackId }),
        }
      ),

    listAssessments: (tenderId?: string) => {
      const q = tenderId ? `?tender_id=${encodeURIComponent(tenderId)}` : "";
      return this.request<{ results?: VerificationAssessmentRecord[] } | VerificationAssessmentRecord[]>(
        `/api/v1/verify/assessments/${q}`
      );
    },

    getAssessment: (id: string) =>
      this.request<VerificationAssessmentRecord>(`/api/v1/verify/assessments/${encodeURIComponent(id)}/`),

    overrideVerdict: (assessmentId: string, ruleId: string, newVerdict: "PASS" | "FAIL" | "WAIVED", reason: string) =>
      this.request<{ success: boolean; message: string; override: any; assessment: VerificationAssessmentRecord }>(
        `/api/v1/verify/assessments/${encodeURIComponent(assessmentId)}/override/`,
        {
          method: "POST",
          body: JSON.stringify({ rule_id: ruleId, new_verdict: newVerdict, reason }),
        }
      ),

    dossier: (tenderId?: string, assessmentId?: string) => {
      const q = new URLSearchParams();
      if (tenderId) q.set("tender_id", tenderId);
      if (assessmentId) q.set("assessment_id", assessmentId);
      const qs = q.toString() ? `?${q.toString()}` : "";
      return this.request<ComplianceDossierRecord>(`/api/v1/verify/dossier/${qs}`);
    },

    dossierPdfUrl: (tenderId?: string, assessmentId?: string) => {
      const q = new URLSearchParams();
      if (tenderId) q.set("tender_id", tenderId);
      if (assessmentId) q.set("assessment_id", assessmentId);
      const qs = q.toString() ? `?${q.toString()}` : "";
      return `/api/backend/api/v1/verify/dossier/pdf/${qs}`;
    },
  };

  // --- 6. Immutable Audit Trail ---
  public audit = {
    list: (params: { target_id?: string; event_type?: string; page?: number } = {}) => {
      const q = new URLSearchParams();
      if (params.target_id) q.set("target_id", params.target_id);
      if (params.event_type) q.set("event_type", params.event_type);
      if (params.page) q.set("page", String(params.page));
      return this.request<{ results?: AuditEntry[]; count?: number } | AuditEntry[]>(
        `/api/v1/audit/?${q.toString()}`
      );
    },

    get: (id: string) => this.request<AuditEntry>(`/api/v1/audit/${encodeURIComponent(id)}/`),
  };

  // --- 7. Async Background Jobs ---
  public jobs = {
    get: (id: string) => this.request<AsyncJobStatus>(`/api/v1/jobs/${encodeURIComponent(id)}/`),

    poll: async (
      id: string,
      onProgress?: (job: AsyncJobStatus) => void,
      maxAttempts = 30,
      intervalMs = 1500
    ): Promise<AsyncJobStatus> => {
      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        const job = await apiClient.jobs.get(id);
        if (onProgress) onProgress(job);

        if (job.status === "COMPLETED" || job.status === "FAILED") {
          return job;
        }

        const backoff = Math.min(intervalMs * Math.pow(1.15, attempt), 6000);
        await new Promise((r) => setTimeout(r, backoff));
      }
      throw new Error("Job processing timed out.");
    },
  };

  // --- 8. Grounded Evidence Citations ---
  public evidence = {
    list: (params: { document_id?: string; field_key?: string } = {}) => {
      const q = new URLSearchParams();
      if (params.document_id) q.set("document_id", params.document_id);
      if (params.field_key) q.set("field_key", params.field_key);
      const queryStr = q.toString() ? `?${q.toString()}` : "";
      return this.request<EvidenceCitationRecord[]>(`/api/v1/evidence/${queryStr}`);
    },
  };
}

export const apiClient = new APIClient();
export default apiClient;
