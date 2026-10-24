import React from "react";
import Sidebar from "@/components/Sidebar";
import DashboardHeader from "@/components/DashboardHeader";
import AuditHeaderStrip from "@/components/AuditHeaderStrip";
import ReadinessGaugeCard from "@/components/ReadinessGaugeCard";
import RegulatoryBento from "@/components/RegulatoryBento";
import VerificationMatrix from "@/components/VerificationMatrix";
import RemediationRoadmap from "@/components/RemediationRoadmap";
import EvidenceInspector from "@/components/EvidenceInspector";
import AuditBottomBar from "@/components/AuditBottomBar";

export default function AuditPage() {
  return (
    <div className="bg-surface font-sans text-on-surface antialiased min-h-screen">
      {/* Sidebar Navigation */}
      <Sidebar activeTab="audit" />

      {/* Main Content Area */}
      <div className="lg:pl-72 flex flex-col min-h-screen">
        <DashboardHeader />

        <main className="w-full pt-16 bg-surface min-h-screen">
          <div className="px-4 sm:px-8 lg:px-10 py-6 flex flex-col gap-6 max-w-[1440px] mx-auto w-full pb-36">
            {/* Section 1: Tender Context Selector & Header Strip */}
            <AuditHeaderStrip />

            {/* Section 2: Primary Scorecard & Rule Bento */}
            <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
              <div className="lg:col-span-8">
                <ReadinessGaugeCard />
              </div>
              <div className="lg:col-span-4">
                <RegulatoryBento />
              </div>
            </section>

            {/* Section 3: 5-Layer Statutory Verification Matrix */}
            <VerificationMatrix />

            {/* Section 4 & 5: Remediation Roadmap & Evidence Inspector Split */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-7">
                <RemediationRoadmap />
              </div>
              <div className="lg:col-span-5">
                <EvidenceInspector />
              </div>
            </div>

            {/* Section 6: Sticky Submission Bottom Action Bar */}
            <AuditBottomBar />
          </div>
        </main>
      </div>
    </div>
  );
}
