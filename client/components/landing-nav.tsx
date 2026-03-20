import Link from "next/link"
import { BasketballIcon } from "@/components/basketball-icon"

export function LandingNav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <BasketballIcon className="h-6 w-6 text-primary" />
          <span className="text-lg font-semibold tracking-tight text-foreground">
            AIrBall
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <Link
            href="/auth/login"
            className="rounded-md px-4 py-2 text-sm font-medium text-foreground transition-colors hover:text-primary"
          >
            Sign in
          </Link>
          <Link
            href="/auth/sign-up"
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Get started
          </Link>
        </div>
      </div>
    </nav>
  )
}
