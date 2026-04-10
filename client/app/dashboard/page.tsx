import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { DashboardNav } from "@/components/dashboard-nav"
import { VideoUploader } from "@/components/video-uploader"
import { VideoList } from "@/components/video-list"
import { DashboardStats } from "@/components/dashboard-stats"

export default async function DashboardPage() {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  const firstName =
    user.user_metadata?.full_name?.split(" ")[0] ??
    user.email?.split("@")[0] ??
    "there"

  return (
    <div className="min-h-screen bg-background">
      <DashboardNav userEmail={user.email ?? ""} />
      <main className="mx-auto max-w-5xl px-6 py-10">
        {/* Welcome Banner */}
        <div className="mb-8 rounded-xl border border-border bg-card p-6">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Welcome back, {firstName} 👋
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Upload a video of your basketball shot and let AI analyze your form.
          </p>
        </div>

        {/* Stats */}
        <DashboardStats />

        {/* Upload Section */}
        <div className="mb-8">
          <h2 className="mb-3 text-lg font-semibold text-foreground">
            Upload New Shot
          </h2>
          <VideoUploader userId={user.id} />
        </div>

        {/* Videos Section */}
        <div>
          <h2 className="mb-3 text-lg font-semibold text-foreground">
            Your Shots
          </h2>
          <VideoList />
        </div>
      </main>
    </div>
  )
}