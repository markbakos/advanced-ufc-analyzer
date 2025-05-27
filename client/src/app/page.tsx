import Link from "next/link"
import {ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import UnauthHeader from "@/components/mainpage/unauth-header"
import PredictionsSection from "@/components/mainpage/predictions-section";
import HowItWorksSection from "@/components/mainpage/hiw-section";
import Footer from "@/components/mainpage/footer";

export default function Home() {
  return (
      <div className="flex min-h-screen flex-col">
        <UnauthHeader />
        <main className="flex-1">
          <section className="relative w-full min-h-[100vh] bg-gradient-to-br from-gray-50 to-white text-gray-900 overflow-hidden">
            <div className="absolute inset-0">
              <div className="absolute inset-0 bg-gradient-to-br from-red-200/50 via-white to-gray-50" />
              <div className="absolute top-0 right-0 w-full sm:w-3/4 lg:w-1/2 h-full bg-gradient-to-l from-red-200/30 to-transparent" />
            </div>

            <div className="container relative z-10 px-4 sm:px-6 lg:px-8 min-h-screen flex items-center">
              <div className="w-full">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center">
                  <div className="flex flex-col justify-center space-y-6 sm:space-y-8 order-1 lg:order-1">
                    <div className="flex items-center justify-center lg:justify-start">
                      <div className="flex items-center gap-2 bg-red-600/20 border border-red-600/30 rounded-full px-3 py-2 sm:px-4">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                        <span className="text-xs sm:text-sm font-medium text-red-600">Free Predictions Available</span>
                      </div>
                    </div>

                    <div className="space-y-4 sm:space-y-6 text-center lg:text-left">
                      <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold tracking-tight leading-tight">
                        <span className="block">Predict UFC Fights</span>
                        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-red-300">
                        Like a Champion
                      </span>
                      </h1>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 py-4 sm:py-6">
                      <div className="text-center lg:text-left bg-white/50 rounded-lg p-3 sm:p-4 lg:bg-transparent lg:p-0">
                        <div className="text-2xl sm:text-3xl lg:text-3xl xl:text-4xl font-bold text-red-500">75%</div>
                        <div className="text-xs sm:text-sm text-gray-500">Prediction Accuracy</div>
                      </div>
                      <div className="text-center lg:text-left bg-white/50 rounded-lg p-3 sm:p-4 lg:bg-transparent lg:p-0">
                        <div className="text-2xl sm:text-3xl lg:text-3xl xl:text-4xl font-bold text-red-500">15K+</div>
                        <div className="text-xs sm:text-sm text-gray-500">Fights Trained On</div>
                      </div>
                      <div className="text-center lg:text-left bg-white/50 rounded-lg p-3 sm:p-4 lg:bg-transparent lg:p-0">
                        <div className="text-2xl sm:text-3xl lg:text-3xl xl:text-4xl font-bold text-red-500">4000+</div>
                        <div className="text-xs sm:text-sm text-gray-500">Fighters Available</div>
                      </div>
                    </div>

                    <div className="flex justify-center lg:justify-start">
                      <Link href="/signup" className="w-full sm:w-auto">
                        <Button
                            size="lg"
                            className="w-full sm:w-auto bg-red-600 hover:bg-red-700 text-white cursor-pointer px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg font-semibold group transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
                        >
                          Start Predicting Free
                          <ChevronRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                        </Button>
                      </Link>
                    </div>
                  </div>

                  <div className="relative order-2 lg:order-2 mt-8 lg:mt-0">
                    <div className="relative max-w-lg mx-auto lg:max-w-none">
                      <div className="flex justify-center z-10">
                        <div className="w-1/2 h-64 flex justify-center items-center flex-col p-10 space-y-2">
                          <h2 className="text-semibold text-lg">
                            Last PPV:
                          </h2>
                          <h1 className="text-4xl font-bold">
                            UFC 315
                          </h1>
                          <p className="text-2xl text-green-400">
                            +7.5 Units
                          </p>
                        </div>
                      </div>
                      <div className="absolute -bottom-2 right-16 sm:-bottom-4 sm:-right-4 lg:-bottom-6 lg:right-28 z-20">
                        <div className="bg-white/90 backdrop-blur-sm border border-red-200/50 rounded-lg sm:rounded-xl p-2 sm:p-3 lg:p-4 shadow-lg sm:shadow-xl">
                          <div className="text-center">
                            <div className="text-lg sm:text-xl lg:text-2xl font-bold text-red-500">85%</div>
                            <div className="text-xs text-gray-500">Accuracy</div>
                          </div>
                        </div>
                      </div>

                      <div className="absolute inset-0 -z-10">
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 sm:w-80 sm:h-80 lg:w-96 lg:h-96 bg-red-600/20 rounded-full blur-2xl sm:blur-3xl" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="absolute bottom-4 sm:bottom-8 hidden md:block left-1/2 transform -translate-x-1/2 z-10">
              <div className="flex flex-col items-center gap-1 sm:gap-2 text-gray-500">
                <span className="text-xs sm:text-sm">Scroll to explore</span>
                <div className="w-5 h-8 sm:w-6 sm:h-10 border-2 border-gray-300 rounded-full flex justify-center">
                  <div className="w-1 h-2 sm:h-3 bg-gray-400 rounded-full mt-1 sm:mt-2 animate-bounce" />
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
