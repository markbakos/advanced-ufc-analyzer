"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Menu, Trophy } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

export default function UnauthHeader() {
    const [isScrolled, setIsScrolled] = useState(false)
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
    const [scrollWidth, setScrollWidth] = useState(0)

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10)
        }

        window.addEventListener("scroll", handleScroll)
    }, [])

    useEffect(() => {
        const calculateScrollWidth = () => {
            setScrollWidth(Math.min(((window?.scrollY || 0) / (document?.documentElement?.scrollHeight - window?.innerHeight || 1)) * 100, 100))
        }

        window.addEventListener("scroll", calculateScrollWidth)
    }, []);

    const navigationItems = [
        { name: "Home", href: "/", active: true },
        { name: "Predictions", href: "#predictions" },
        { name: "How It Works", href: "#how-it-works" },
    ]

    return (
        <header
            className={`fixed top-0 z-50 w-screen transition-all duration-300 ${
                isScrolled
                    ? "bg-white/95 backdrop-blur-md shadow-lg border-b border-gray-200/50"
                    : "bg-white/90 backdrop-blur-sm border-b border-gray-100"
            }`}
        >
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 lg:h-20 items-center justify-between">
                    {/* logo */}
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="relative">
                            <Trophy className="h-7 w-7 lg:h-8 lg:w-8 text-red-600 transition-transform group-hover:scale-110" />
                            <div className="absolute inset-0 bg-red-600/20 rounded-full blur-sm opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        <span className="text-xl lg:text-2xl font-bold text-gray-900 tracking-tight">UFC Predictor</span>
                    </Link>

                    {/* desktop navigation */}
                    <nav className="hidden lg:flex items-center space-x-1">
                        {navigationItems.map((item) => (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`relative px-4 py-2 text-sm font-medium transition-all duration-200 rounded-lg group ${
                                    item.active ? "text-red-600 bg-red-50" : "text-gray-700 hover:text-red-600 hover:bg-gray-50"
                                }`}
                            >
                                {item.name}
                                {item.active && (
                                    <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-red-600 rounded-full" />
                                )}
                                <div className="absolute inset-0 bg-red-600/5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity" />
                            </Link>
                        ))}
                    </nav>

                    {/* desktop auth buttons */}
                    <div className="hidden lg:flex items-center gap-3">
                        <Link
                            href="/signin"
                            className="text-sm font-medium text-gray-700 hover:text-red-600 transition-colors px-4 py-2 rounded-lg hover:bg-gray-50"
                        >
                            Sign In
                        </Link>
                        <Button
                            asChild
                            className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 text-sm font-semibold transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl"
                        >
                            <Link href="/signup">Get Started</Link>
                        </Button>
                    </div>

                    {/* mobile menu button */}
                    <div className="lg:hidden">
                        <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
                            <SheetTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="p-2 hover:bg-gray-100 transition-colors"
                                    aria-label="Toggle mobile menu"
                                >
                                    <Menu className="h-6 w-6 text-gray-700" />
                                </Button>
                            </SheetTrigger>
                            <SheetContent side="right" className="w-screen sm:w-80 p-0">
                                <div className="flex flex-col h-full">
                                    {/* mobile header */}
                                    <div className="flex items-center justify-between p-6 border-b border-gray-100">
                                        <Link href="/" className="flex items-center gap-2" onClick={() => setIsMobileMenuOpen(false)}>
                                            <Trophy className="h-6 w-6 text-red-600" />
                                            <span className="text-lg font-bold text-gray-900">UFC Predictor</span>
                                        </Link>
                                    </div>

                                    {/* mobile navigation */}
                                    <nav className="flex-1 px-6 py-6">
                                        <div className="space-y-2">
                                            {navigationItems.map((item) => (
                                                <Link
                                                    key={item.name}
                                                    href={item.href}
                                                    onClick={() => setIsMobileMenuOpen(false)}
                                                    className={`flex items-center justify-between w-full px-4 py-3 text-base font-medium rounded-xl transition-all duration-200 ${
                                                        item.active
                                                            ? "text-red-600 bg-red-50 border border-red-100"
                                                            : "text-gray-700 hover:text-red-600 hover:bg-gray-50"
                                                    }`}
                                                >
                                                    {item.name}
                                                    {item.active && <div className="w-2 h-2 bg-red-600 rounded-full" />}
                                                </Link>
                                            ))}
                                        </div>

                                        {/* mobile auth section */}
                                        <div className="mt-8 pt-6 border-t border-gray-100 space-y-3">
                                            <Button
                                                asChild
                                                variant="outline"
                                                className="w-full justify-center py-3 text-base font-medium border-gray-200 hover:bg-gray-50"
                                            >
                                                <Link href="/signin" onClick={() => setIsMobileMenuOpen(false)}>
                                                    Sign In
                                                </Link>
                                            </Button>
                                            <Button
                                                asChild
                                                className="w-full justify-center py-3 text-base font-semibold bg-red-600 hover:bg-red-700 text-white"
                                            >
                                                <Link href="/signup" onClick={() => setIsMobileMenuOpen(false)}>
                                                    Get Started Free
                                                </Link>
                                            </Button>
                                        </div>
                                    </nav>
                                </div>
                            </SheetContent>
                        </Sheet>
                    </div>
                </div>
            </div>

            {/* scroll progress bar  */}
            <div className="absolute bottom-0 left-0 w-full h-0.5 bg-gray-100">
                <div
                    className="h-full bg-gradient-to-r from-red-500 to-red-600 transition-all duration-300"
                    style={{
                        width: `${scrollWidth}%`,
                    }}
                />
            </div>
        </header>
    )
}
