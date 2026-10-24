"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

interface SidebarProps {
  activeTab?: string;
  activeRoute?: string;
}

export default function Sidebar({ activeTab, activeRoute }: SidebarProps) {
  const pathname = usePathname();

  const isCurrent = (path: string, tabName: string) => {
    if (activeRoute && (activeRoute === path || activeRoute === tabName)) return true;
    if (activeTab === tabName) return true;
    if (path === pathname) return true;
    return false;
  };

  const navItems = [
    { name: "Dashboard", path: "/dashboard", tab: "dashboard", icon: "grid_view" },
    { name: "Open Tenders", path: "/tenders", tab: "tenders", icon: "gavel" },
    { name: "Document Vault", path: "/vault", tab: "vault", icon: "folder_managed" },
    { name: "Bid Readiness & Audits", path: "/audit", tab: "audit", icon: "verified_user" },
    { name: "Corrigendum Radar", path: "/corrigendum", tab: "corrigendum", icon: "radar" },
    { name: "Settings", path: "/settings", tab: "settings", icon: "settings" },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-72 bg-surface-container-low flex flex-col justify-between py-6 px-4 z-50 shadow-[0_1px_8px_rgba(0,0,0,0.04)] border-r border-outline-variant/30 hidden lg:flex">
      <div className="flex flex-col gap-6">
        {/* Brand Logo & Intelligence Tagline with Official logo.png */}
        <Link href="/" className="flex items-center gap-3 px-2 group">
          <div className="w-10 h-10 rounded-xl overflow-hidden flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform shadow-xs">
            <Image
              src="/logo.png"
              alt="TenderBee"
              width={40}
              height={40}
              className="w-full h-full object-contain"
              priority
            />
          </div>
          <div className="flex flex-col">
            <span className="font-serif text-2xl font-bold tracking-tight text-primary leading-none">
              Tender<span className="text-secondary">Bee</span>
            </span>
            <span className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-widest mt-1">
              Compliance Intelligence
            </span>
          </div>
        </Link>

        {/* Autonomous Radar Status Pill */}
        <div className="px-1">
          <div className="bg-surface-container rounded-xl p-2.5 flex items-center justify-between border border-outline-variant/20">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
              <span className="text-xs text-on-surface font-semibold">Autonomous Radar</span>
            </div>
            <span className="text-[10px] font-bold bg-surface-container-lowest text-primary px-2 py-0.5 rounded-full border border-primary/10">
              v2.4 Active
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-1.5">
          {navItems.map((item) => {
            const active = isCurrent(item.path, item.tab);
            return (
              <Link
                key={item.tab}
                href={item.path}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl transition-all text-sm font-medium ${
                  active
                    ? "bg-primary text-on-primary font-semibold shadow-sm"
                    : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface"
                }`}
              >
                <span className="material-symbols-outlined text-xl">{item.icon}</span>
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Sync Information Card */}
      <div className="flex flex-col gap-3 px-1">
        <div className="p-3.5 rounded-xl bg-surface-container-lowest shadow-[0_12px_32px_-4px_rgba(59,0,102,0.08)] border border-outline-variant/30 flex flex-col gap-1.5">
          <div className="flex items-center gap-2 text-secondary">
            <span className="material-symbols-outlined text-lg">hub</span>
            <span className="text-[11px] uppercase tracking-wider font-bold text-secondary">
              Portal Sync
            </span>
          </div>
          <p className="text-xs text-on-surface-variant leading-snug">
            CPPP eProcurement &amp; GeM nodes verified 4m ago.
          </p>
          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] font-medium text-on-surface-variant">Status: Green</span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm" />
          </div>
        </div>

        <div className="text-center py-1">
          <span className="text-[10px] tracking-wider uppercase font-semibold text-outline">
            Institutional Enterprise Tier
          </span>
        </div>
      </div>
    </aside>
  );
}
