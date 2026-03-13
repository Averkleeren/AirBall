import Link from "next/link"

export function HeroSection() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center px-6 pt-20">
      <div className="mx-auto max-w-3xl text-center">
        <p className="mb-4 text-sm font-medium uppercase tracking-widest text-primary">
          AI-Powered Shot Analysis
        </p>
        <h1 className="text-balance text-5xl font-bold leading-tight tracking-tight text-foreground md:text-7xl">
          AirBalling?{" "}
          <br className="hidden md:block" />
          Try using{" "}
          <span className="text-primary">AIrBall!</span>
        </h1>
        <p className="mx-auto mt-6 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
          Upload a video of your basketball shot and let AI break down your
          form. Get instant feedback on arc, release speed, and follow-through.
        </p>
        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Link
            href="/auth/sign-up"
            className="w-full rounded-md bg-primary px-8 py-3 text-center text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 sm:w-auto"
          >
            Start analyzing for free
          </Link>
          <Link
            href="#how-it-works"
            className="w-full rounded-md border border-border px-8 py-3 text-center text-sm font-medium text-foreground transition-colors hover:bg-secondary sm:w-auto"
          >
            See how it works
          </Link>
        </div>
      </div>

      {/* Hero image */}
      <div className="mx-auto mt-16 w-full max-w-4xl overflow-hidden rounded-xl border border-border shadow-lg">
        <img
          src="/images/hero-basketball.jpg"
          alt="Basketball going through a hoop, viewed from below against blue sky"
          className="h-auto w-full object-cover"
          loading="eager"
        />
      </div>
    </section>
  )
}
