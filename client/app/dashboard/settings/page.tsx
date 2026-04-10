import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { DashboardNav } from "@/components/dashboard-nav"
import { SettingsForm } from "@/components/settings-form"

export default async function SettingsPage() {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  return (
    <div className="min-h-screen bg-background">
      <DashboardNav userEmail={user.email ?? ""} />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Settings
          </h1>
          <p className="mt-1.5 text-muted-foreground">
            Manage your account and preferences.
          </p>
        </div>

        <div className="flex flex-col gap-6">
          {/* Account */}
          <div className="rounded-xl border border-border bg-card p-8">
            <h2 className="mb-5 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Account
            </h2>
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-card-foreground">Email address</p>
                  <p className="mt-0.5 text-sm text-muted-foreground">{user.email}</p>
                </div>
              </div>
              <div className="border-t border-border" />
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-card-foreground">Account ID</p>
                  <p className="mt-0.5 font-mono text-xs text-muted-foreground">{user.id}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Appearance */}
          <SettingsForm />
        </div>
      </main>
    </div>
  )
}
