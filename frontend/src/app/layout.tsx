import type { Metadata } from "next";
import { Inter, Newsreader } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const newsreader = Newsreader({
  subsets: ["latin"],
  variable: "--font-newsreader",
  style: ["normal", "italic"],
  display: "swap",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "TenderBee — Find the Right Tenders. Bid with Confidence.",
  description:
    "Discover relevant opportunities, verify compliance, understand eligibility, and stay prepared with intelligent tender insights across GeM, CPPP, and state procurement portals.",
  keywords: [
    "TenderBee",
    "Bid Verification",
    "GeM Portal",
    "CPPP eProcurement",
    "Government Tenders India",
    "Compliance Intelligence",
    "Tender Eligibility",
  ],
  authors: [{ name: "TenderBee Technologies Inc." }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${newsreader.variable}`}>
      <body className="font-sans antialiased selection:bg-brand-purple selection:text-white">
        {children}
      </body>
    </html>
  );
}
