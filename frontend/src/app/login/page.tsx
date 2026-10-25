"use client";

import React, { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTarget = searchParams.get("from") || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    // Client-side validation
    if (!email || !email.includes("@")) {
      setErrorMessage("Please enter a valid email address.");
      return;
    }
    if (!password || password.length < 6) {
      setErrorMessage("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    try {
      const res = await apiClient.auth.login({ email, password });
      if (res.success) {
        router.push(redirectTarget);
        router.refresh();
      } else {
        setErrorMessage("Authentication failed. Please verify your credentials.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-[#eef2f6]">
      <div className="w-full max-w-md p-8 rounded-3xl neu-card neu-depth">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl neu-inset mb-4 text-amber-500 font-black text-2xl">
            TB
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Welcome to TenderBee</h1>
          <p className="text-sm text-slate-500 mt-1">Deterministic Tender Verification & Intake</p>
        </div>

        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl neu-inset border border-rose-200 bg-rose-50/50 text-rose-700 text-sm flex items-center gap-2">
            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-2">
              Work Email Address
            </label>
            <input
              id="login-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="bid.officer@domain.gov.in"
              className="w-full px-4 py-3 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 transition-all text-sm"
              disabled={loading}
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600">
                Password
              </label>
            </div>
            <div className="relative">
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-4 py-3 pr-11 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 transition-all text-sm"
                disabled={loading}
              />
              <button
                type="button"
                id="toggle-login-password"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700 p-1 focus:outline-none cursor-pointer"
                aria-label={showPassword ? "Hide password" : "Show password"}
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            id="login-submit-btn"
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-xl neu-button text-slate-800 font-semibold text-sm transition-all flex items-center justify-center gap-2 hover:text-amber-600 active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-amber-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Sign In with Credentials</span>
            )}
          </button>

          <div className="relative flex py-1 items-center">
            <div className="flex-grow border-t border-slate-300/60"></div>
            <span className="flex-shrink mx-3 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">or instant demo</span>
            <div className="flex-grow border-t border-slate-300/60"></div>
          </div>

          <button
            type="button"
            id="demo-login-btn"
            disabled={loading}
            onClick={async () => {
              setEmail("demo@tenderbee.ai");
              setPassword("password123");
              setLoading(true);
              setErrorMessage("");
              try {
                const res = await apiClient.auth.login({ email: "demo@tenderbee.ai", password: "password123" });
                if (res.success) {
                  router.push(redirectTarget);
                  router.refresh();
                } else {
                  setErrorMessage("Demo authentication failed.");
                }
              } catch (err: any) {
                setErrorMessage(err.message || "Failed to log in with demo account.");
              } finally {
                setLoading(false);
              }
            }}
            className="w-full py-3 px-6 rounded-xl border border-amber-400/40 bg-amber-500/10 text-amber-700 font-bold text-xs uppercase tracking-wider hover:bg-amber-500/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
            <span>1-Click Demo Sign-In (Preloaded Tenant)</span>
          </button>
        </form>


        <div className="mt-8 pt-6 border-t border-slate-200/50 text-center">
          <p className="text-xs text-slate-500">
            Don't have a tenant organization?{" "}
            <Link href="/register" className="font-semibold text-amber-600 hover:underline">
              Register New Organization
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-[#eef2f6] text-slate-500">Loading auth...</div>}>
      <LoginForm />
    </Suspense>
  );
}
