import { Button } from '@/components/ui/button'
import Image from 'next/image'
import { ChevronRight } from 'lucide-react'
import Link from "next/link";


export default function HowItWorksSection() {
    return (
        <section id="howitworks" className="w-full py-12 md:py-24 lg:py-32 bg-gray-50">
            <div className="container px-4 md:px-6">
                <div className="grid gap-10 lg:grid-cols-2 items-center">
                    <div className="space-y-4">
                        <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Why Choose Our Prediction System?</h2>
                        <p className="text-muted-foreground md:text-xl">
                            Our advanced prediction system is designed to provide you with the most accurate fight predictions.
                        </p>
                        <ul className="grid gap-4">
                            <li className="flex items-start gap-2">
                                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-red-600 text-white">
                                    <ChevronRight className="h-4 w-4" />
                                </div>
                                <div>
                                    <h3 className="font-medium">Data-Driven Analysis</h3>
                                    <p className="text-sm text-muted-foreground">
                                        We analyze hundreds of data points from fighter statistics, historical matchups, and
                                        performance metrics.
                                    </p>
                                </div>
                            </li>
                            <li className="flex items-start gap-2">
                                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-red-600 text-white">
                                    <ChevronRight className="h-4 w-4" />
                                </div>
                                <div>
                                    <h3 className="font-medium">Community</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Join a community of fight enthusiasts and analysts, chat and share fight predictions.
                                    </p>
                                </div>
                            </li>
                            <li className="flex items-start gap-2">
                                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-red-600 text-white">
                                    <ChevronRight className="h-4 w-4" />
                                </div>
                                <div>
                                    <h3 className="font-medium">High Accuracy</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Our prediction models show an accuracy of 75% correct result prediction and 50% method prediction, while our advanced model improve upon this.
                                    </p>
                                </div>
                            </li>
                        </ul>
                        <Link href="/signup">
                            <Button variant="outline" className="mt-4">
                                Join the Community
                            </Button>
                        </Link>
                    </div>
                    <div className="relative">
                        <Image
                            src="/placeholder.svg?height=500&width=500"
                            width={500}
                            height={500}
                            alt="UFC fight analysis"
                            className="mx-auto rounded-xl"
                        />
                    </div>
                </div>
            </div>
        </section>
    )
}