"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { BasketballIcon } from "@/components/basketball-icon";
import { Button } from "@/components/ui/button";

export default function SignUpSuccessPage() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email");
  const username = searchParams.get("username");

  return (
    <div className="flex min-h-svh w-full items-center justify-center bg-background px-6">
      <div className="w-full max-w-md rounded-xl border border-border bg-card p-8 text-center">
        <div className="mb-8 flex justify-center">
          <Link href="/" className="inline-flex items-center gap-2">
            <BasketballIcon className="h-7 w-7 text-primary" />
            <span className="text-xl font-semibold tracking-tight text-foreground">
              AIrBall
            </span>
          </Link>
        </div>

        <h1 className="text-2xl font-bold text-card-foreground">
          Verify your email
        </h1>
        <p className="mt-3 text-sm text-muted-foreground">
          {username ? `Thanks, ${username}. ` : ""}
          We sent a verification link
          {email ? ` to ${email}` : " to your inbox"}. Open it before signing
          in.
        </p>

        <div className="mt-6 rounded-lg border border-border bg-muted/40 p-4 text-left text-sm text-muted-foreground">
          <p>Next steps:</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            <li>Check your inbox and spam folder.</li>
            <li>Click the verification link in the email.</li>
            <li>Return to login after verification completes.</li>
          </ul>
        </div>

        {email && (
          <p className="mt-4 text-sm text-muted-foreground">
            Need another email? Open the resend verification page and use the
            same address.
          </p>
        )}

        <div className="mt-6 flex flex-col gap-3">
          <Button asChild>
            <Link
              href={`/auth/login${email ? `?email=${encodeURIComponent(email)}` : ""}`}
            >
              Go to login
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link
              href={`/auth/resend-verification${email ? `?email=${encodeURIComponent(email)}` : ""}`}
            >
              Resend verification email
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/auth/signup">Create another account</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
