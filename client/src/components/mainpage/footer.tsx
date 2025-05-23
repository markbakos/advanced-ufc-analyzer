import { Trophy } from "lucide-react";
import Link from "next/link";

export default function Footer() {
    return (
        <footer className="w-full border-t py-6 md:py-0">
            <div className="container flex flex-col md:flex-row md:h-16 items-center justify-between gap-4 md:gap-0">
                <Link href="/">
                    <div className="flex items-center gap-2 px-0 lg:px-10">
                        <Trophy className="h-5 w-5 text-red-600" />
                        <span className="font-semibold">UFC Predictor</span>
                    </div>
                </Link>
                <div className="text-center md:text-left text-sm text-muted-foreground">
                    © 2025 UFC Predictor. All rights reserved.
                </div>
                <nav className="flex gap-4 sm:gap-6">
                    <Link href="https://github.com/markbakos" target="_blank" className="text-xs text-muted-foreground underline-offset-4 hover:underline">
                        Github
                    </Link>
                    <Link href="https://markbakos.com" target="_blank" className="text-xs text-muted-foreground underline-offset-4 hover:underline">
                        Personal Website
                    </Link>
                </nav>
            </div>
        </footer>
    )
}