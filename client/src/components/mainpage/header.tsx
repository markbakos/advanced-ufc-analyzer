import {Trophy} from "lucide-react";
import Link from "next/link";
import {Button} from "@/components/ui/button";

export default function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-16 items-center justify-between">
                <Link href="/client/public">
                    <div className="flex items-center gap-2 px-2 lg:px-8">
                        <Trophy className="h-6 w-6 text-red-600" />
                        <span className="text-xl font-bold">UFC Predictor</span>
                    </div>
                </Link>
                <nav className="hidden md:flex gap-6">
                    <Link href="#" className="text-sm font-medium transition-colors hover:text-primary">
                        Home
                    </Link>
                    <Link href="#predictions" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                        Predictions
                    </Link>
                    <Link href="#howitworks" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                        How It Works
                    </Link>
                    <Link href="#about" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                        About
                    </Link>
                </nav>
                <div className="flex items-center gap-4 px-2 lg:px-0">
                    <Link href="/signin" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
                        Sign In
                    </Link>
                    <Link href="/signup">
                        <Button>Sign Up</Button>
                    </Link>

                </div>
            </div>
        </header>
    )
}