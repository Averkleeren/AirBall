"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { BasketballIcon } from "@/components/basketball-icon";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { API_ENDPOINTS, apiCall } from "@/lib/api";

export default function ResendVerificationPage() {
  const searchParams = useSearchParams();

  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const initialEmail = searchParams.get("email");

    if (initialEmail) {
      setEmail(initialEmail);
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setMessage(null);

    const result = await apiCall<{ message: string }>(
      API_ENDPOINTS.resendVerification,
      {
        method: "POST",
        body: JSON.stringify({
          email,
          email_redirect_to: `${window.location.origin}/auth/login?verified=1`,
        }),
      },
    );

    if (!result.ok) {
      setError(result.error || "Failed to resend verification email.");
      setIsLoading(false);
      return;
    }

    setMessage(
      result.data?.message ||
        "Verification email resent if the signup request exists.",
    );
    setIsLoading(false);
  };

  return (
    <div className="flex min-h-svh w-full items-center justify-center bg-background px-6">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <Link href="/" className="inline-flex items-center gap-2">
            <BasketballIcon className="h-7 w-7 text-primary" />
            <span className="text-xl font-semibold tracking-tight text-foreground">
              AIrBall
            </span>
          </Link>
        </div>

        <div className="rounded-xl border border-border bg-card p-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-card-foreground">
              Resend verification email
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Enter the email used at signup and we’ll send a new verification
              link.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <div className="flex flex-col gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}
            {message && <p className="text-sm text-green-600">{message}</p>}

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Sending..." : "Resend verification"}
            </Button>
          </form>

          <div className="mt-6 space-y-2 text-center text-sm text-muted-foreground">
            <p>
              <Link
                href="/auth/login"
                className="font-medium text-primary hover:underline"
              >
                Back to login
              </Link>
            </p>
            <p>
              <Link
                href="/auth/signup"
                className="font-medium text-primary hover:underline"
              >
                Back to sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
