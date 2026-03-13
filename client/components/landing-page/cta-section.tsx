import Link from "next/link"

export function CTASection() {
  return (
    <section className="px-6 py-32">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="text-balance text-3xl font-bold tracking-tight text-foreground md:text-4xl">
          Ready to improve your game?
        </h2>
        <p className="mx-auto mt-4 max-w-md text-muted-foreground">
          Join players who use AI to perfect their shot. It takes less than a
          minute to get started.
        </p>
        <div className="mt-8">
          <Link
            href="/auth/sign-up"
            className="inline-block rounded-md bg-primary px-8 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Create free account
          </Link>
        </div>
      </div>
    </section>
  )
}
