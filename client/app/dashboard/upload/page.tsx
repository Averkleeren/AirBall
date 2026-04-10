import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { DashboardNav } from "@/components/dashboard-nav";
import { VideoUploader } from "@/components/video-uploader";

export default async function UploadPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/auth/login");
  }

  return (
    <div className="min-h-screen bg-background">
      <DashboardNav userEmail={user.email ?? ""} />
      <main className="mx-auto max-w-3xl px-6 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Upload a Shot
          </h1>
          <p className="mt-2 text-muted-foreground">
            Upload a video of your basketball shot and our AI will analyze your
            form, arc, speed, and follow-through.
          </p>
        </div>
        <VideoUploader userId={user.id} />
      </main>
    </div>
  );
}
