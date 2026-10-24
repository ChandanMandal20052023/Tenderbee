import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import TrustStrip from "@/components/TrustStrip";
import FrameworksSection from "@/components/FrameworksSection";
import BuiltForYouSection from "@/components/BuiltForYouSection";
import FeatureGrid from "@/components/FeatureGrid";
import CtaBanner from "@/components/CtaBanner";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />
      <HeroSection />
      <TrustStrip />
      <FrameworksSection />
      <BuiltForYouSection />
      <FeatureGrid />
      <CtaBanner />
      <Footer />
    </main>
  );
}
