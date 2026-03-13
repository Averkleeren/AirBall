import { LandingNav } from "@/components/landing-page/landing-nav"
import { HeroSection } from "@/components/landing-page/hero-section"
import { FeaturesSection } from "@/components/landing-page/features-section"
import { StepsSection } from "@/components/landing-page/steps-section"
import { CTASection } from "@/components/landing-page/cta-section"
import { LandingFooter } from "@/components/landing-page/landing-footer"

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      <LandingNav />
      <HeroSection />
      <FeaturesSection />
      <StepsSection />
    </main>
  )
}
