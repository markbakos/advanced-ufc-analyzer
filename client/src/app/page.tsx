import Link from "next/link"
import {ChevronRight, TrendingUp} from "lucide-react"
import { Button } from "@/components/ui/button"
import Header from "@/components/mainpage/header"
import PredictionsSection from "@/components/mainpage/predictions-section";
import HowItWorksSection from "@/components/mainpage/hiw-section";
import Footer from "@/components/mainpage/footer";

export default function Home() {
  return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1">
          <section className="w-full min-h-[85vh] py-12 md:py-24 lg:py-32 bg-black text-white">
            <div className="container px-4 md:px-6 relative">
              <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
                <div className="flex flex-col justify-center space-y-4">
                  <div className="space-y-2">
                    <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                      Get High-Accuracy AI Predictions
                    </h1>
                    <p className="max-w-[600px] text-gray-300 md:text-xl">
                      Get access to free UFC Predictions every week and use our private high-accuracy AI model to predict fights between two fighters.
                    </p>
                  </div>
                  <div className="flex gap-2 min-[400px]:flex-row">
                    <Link href="/signup">
                      <Button size="lg" className="bg-red-600 hover:bg-red-700">
                        Get Free Predictions
                        <ChevronRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-300">
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-4 w-4" />
                      <span>75% Accuracy</span>
                    </div>
                  </div>
                </div>
                <div className="relative hidden lg:block">
                {/*  add something here later */}
                </div>
              </div>
            </div>
          </section>

          <PredictionsSection />

          <HowItWorksSection />

          <Footer />

        </main>
      </div>
  )
}
