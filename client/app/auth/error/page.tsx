import { BasketballIcon } from "@/components/basketball-icon"
import Link from "next/link"

export default async function AuthErrorPage({
  searchParams,
}: {
  searchParams: Promise<{ error: string }>
}) {
  const params = await searchParams

  return (
    <div className="flex min-h-svh w-full items-center justify-center bg-background px-6">
      <div className="w-full max-w-sm text-center">
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center gap-2">
            <BasketballIcon className="h-7 w-7 text-primary" />
            <span className="text-xl font-semibold tracking-tight text-foreground">
              AIrBall
            </span>
          </Link>
        </div>

        <div className="rounded-xl border border-border bg-card p-8">
          <h1 className="text-xl font-bold text-card-foreground">
            Something went wrong
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
            {params?.error
              ? `Error: ${params.error}`
              : "An unspecified error occurred."}
          </p>
          <Link
            href="/auth/login"
            className="mt-6 inline-block text-sm font-medium text-primary hover:underline"
          >
            Back to sign in
          </Link>
        </div>
      </div>
    </div>
  )
}
