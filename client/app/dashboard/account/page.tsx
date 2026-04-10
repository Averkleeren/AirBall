import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { DashboardNav } from "@/components/dashboard-nav";
import { AccountSettings } from "@/components/account-settings";

export default async function AccountPage() {
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
      <main className="mx-auto max-w-2xl px-6 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Account Settings
          </h1>
          <p className="mt-2 text-muted-foreground">
            Manage your profile and security preferences.
          </p>
        </div>
        <AccountSettings
          userEmail={user.email ?? ""}
          userId={user.id}
          createdAt={user.created_at}
        />
      </main>
    </div>
  );
}
