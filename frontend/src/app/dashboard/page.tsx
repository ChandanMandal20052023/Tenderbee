import React from "react";
import Sidebar from "@/components/Sidebar";
import DashboardHeader from "@/components/DashboardHeader";
import ExecutiveBanner from "@/components/ExecutiveBanner";
import MetricCards from "@/components/MetricCards";
import TendersList from "@/components/TendersList";
import RemediationRadar from "@/components/RemediationRadar";
import TelemetryFeed from "@/components/TelemetryFeed";

export default function DashboardPage() {
  return (
    <div className="bg-surface font-sans text-on-surface antialiased min-h-screen">
      {/* Sidebar Navigation */}
      <Sidebar activeTab="dashboard" />

      {/* Main Wrapper with desktop sidebar offset */}
      <div className="lg:pl-72 flex flex-col min-h-screen">
        <DashboardHeader />

        <main className="w-full pt-16 bg-surface min-h-screen">
          <div className="flex flex-col w-full max-w-[1500px] mx-auto pb-16">
            {/* Executive Context Bar & Greeting Banner */}
            <ExecutiveBanner />

            {/* Key Metrics Bento Grid */}
            <MetricCards />

            {/* Main Split Layout: Active Tenders vs Remediation Radar */}
            <section className="px-4 sm:px-8 xl:px-12 pb-16 grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
              {/* Left Column: Active Tenders (8 cols) */}
              <div className="xl:col-span-8">
                <TendersList />
              </div>

              {/* Right Column: Remediation Radar & Continuous Audit Stream (4 cols) */}
              <div className="xl:col-span-4 flex flex-col gap-6">
                <RemediationRadar />
                <TelemetryFeed />
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}
