import { BasketballIcon } from "@/components/basketball-icon"

export function LandingFooter() {
  return (
    <footer className="border-t border-border px-6 py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 md:flex-row">
        <div className="flex items-center gap-2 text-muted-foreground">
          <BasketballIcon className="h-5 w-5" />
          <span className="text-sm font-medium">AIrBall</span>
        </div>
        <p className="text-sm text-muted-foreground">
          {"Built with AI. Made for ballers."}
        </p>
      </div>
    </footer>
  )
}
