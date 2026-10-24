"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();

  const [orgName, setOrgName] = useState("");
  const [gstin, setGstin] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    // Client-side validation
    if (!orgName.trim()) {
      setErrorMessage("Organization name is required.");
      return;
    }
    if (!email || !email.includes("@")) {
      setErrorMessage("Please enter a valid work email address.");
      return;
    }
    if (!password || password.length < 8) {
      setErrorMessage("Password must be at least 8 characters long.");
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const res = await apiClient.auth.register({
        organization_name: orgName.trim(),
        gstin: gstin.trim(),
        username: username.trim() || undefined,
        email: email.trim().toLowerCase(),
        password,
      });

      if (res.success) {
        router.push("/dashboard");
        router.refresh();
      } else {
        setErrorMessage("Registration could not be completed.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Registration failed. Please check your information.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-[#eef2f6]">
      <div className="w-full max-w-lg p-8 rounded-3xl neu-card neu-depth">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl neu-inset mb-4 text-amber-500 font-black text-2xl">
            TB
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Register Tenant Organization</h1>
          <p className="text-sm text-slate-500 mt-1">Set up your company workspace and become Owner</p>
        </div>

        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl neu-inset border border-rose-200 bg-rose-50/50 text-rose-700 text-sm flex items-center gap-2">
            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
              Organization / Company Legal Name *
            </label>
            <input
              id="register-org"
              type="text"
              required
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              placeholder="e.g. Apex Infra Projects Private Limited"
              className="w-full px-4 py-2.5 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 text-sm"
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                GSTIN (Optional)
              </label>
              <input
                id="register-gstin"
                type="text"
                value={gstin}
                onChange={(e) => setGstin(e.target.value.toUpperCase())}
                placeholder="27AAAAA0000A1Z5"
                maxLength={15}
                className="w-full px-4 py-2.5 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 text-sm"
                disabled={loading}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Full Name
              </label>
              <input
                id="register-username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Rajesh Kumar"
                className="w-full px-4 py-2.5 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 text-sm"
                disabled={loading}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
              Work Email Address *
            </label>
            <input
              id="register-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="director@apexinfra.co.in"
              className="w-full px-4 py-2.5 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 text-sm"
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Password *
              </label>
              <div className="relative">
                <input
                  id="register-password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 8 characters"
                  className="w-full px-4 py-2.5 pr-10 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 text-sm"
                  disabled={loading}
                />
                <button
                  type="button"
                  id="toggle-register-password"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700 p-1 focus:outline-none cursor-pointer"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5">
                Confirm Password *
              </label>
              <div className="relative">
                <input
                  id="register-confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  className="w-full px-4 py-2.5 pr-10 rounded-xl neu-inset bg-[#eef2f6] text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500/50 text-sm"
                  disabled={loading}
                />
                <button
                  type="button"
                  id="toggle-register-confirm-password"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700 p-1 focus:outline-none cursor-pointer"
                  aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                  title={showConfirmPassword ? "Hide password" : "Show password"}
                >
                  {showConfirmPassword ? (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>

          <button
            type="submit"
            id="register-submit-btn"
            disabled={loading}
            className="w-full mt-2 py-3.5 px-6 rounded-xl neu-button text-slate-800 font-semibold text-sm transition-all flex items-center justify-center gap-2 hover:text-amber-600 active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4 text-amber-500" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>Provisioning Workspace...</span>
              </>
            ) : (
              <span>Create Workspace & Sign In</span>
            )}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-200/50 text-center">
          <p className="text-xs text-slate-500">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-amber-600 hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
