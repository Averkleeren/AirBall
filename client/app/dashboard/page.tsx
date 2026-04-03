import { createClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { DashboardNav } from "@/components/dashboard-nav"
import { VideoUploader } from "@/components/video-uploader"
import { VideoList } from "@/components/video-list"

export default async function DashboardPage() {
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
      <main className="mx-auto max-w-5xl px-6 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Your Shots
          </h1>
          <p className="mt-2 text-muted-foreground">
            Upload a video of your basketball shot and let AI analyze your form.
          </p>
        </div>
        <VideoUploader userId={user.id} />
        <VideoList />
      </main>
    </div>
  )
}