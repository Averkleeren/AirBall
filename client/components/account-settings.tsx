"use client";

import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { Lock, Mail, Calendar, CheckCircle, AlertCircle } from "lucide-react";

type FeedbackState = {
  type: "success" | "error";
  message: string;
} | null;

export function AccountSettings({
  userEmail,
  createdAt,
}: {
  userEmail: string;
  userId: string;
  createdAt: string;
}) {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackState>(null);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    if (newPassword.length < 6) {
      setFeedback({
        type: "error",
        message: "Password must be at least 6 characters.",
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      setFeedback({
        type: "error",
        message: "Passwords do not match.",
      });
      return;
    }

    setIsUpdating(true);
    const supabase = createClient();
    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    });

    if (error) {
      setFeedback({
        type: "error",
        message: error.message || "Failed to update password.",
      });
    } else {
      setFeedback({
        type: "success",
        message: "Password updated successfully.",
      });
      setNewPassword("");
      setConfirmPassword("");
    }

    setIsUpdating(false);
  };

  const memberSince = new Date(createdAt).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Profile Info Card */}
      <div className="rounded-xl border border-border bg-card p-6">
        <h2 className="mb-4 text-lg font-semibold text-card-foreground">
          Profile Information
        </h2>
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-muted">
              <Mail className="h-4 w-4 text-muted-foreground" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Email</p>
              <p className="text-sm font-medium text-foreground">{userEmail}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-muted">
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Member since</p>
              <p className="text-sm font-medium text-foreground">
                {memberSince}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Change Password Card */}
      <div className="rounded-xl border border-border bg-card p-6">
        <div className="mb-4 flex items-center gap-2">
          <Lock className="h-5 w-5 text-muted-foreground" />
          <h2 className="text-lg font-semibold text-card-foreground">
            Change Password
          </h2>
        </div>

        <form onSubmit={handlePasswordChange} className="flex flex-col gap-4">
          <div className="space-y-2">
            <Label htmlFor="new-password">New Password</Label>
            <Input
              id="new-password"
              type="password"
              placeholder="Enter new password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm-password">Confirm New Password</Label>
            <Input
              id="confirm-password"
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {feedback && (
            <div
              className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                feedback.type === "success"
                  ? "bg-green-500/10 text-green-600 dark:text-green-400"
                  : "bg-destructive/10 text-destructive"
              }`}
            >
              {feedback.type === "success" ? (
                <CheckCircle className="h-4 w-4 shrink-0" />
              ) : (
                <AlertCircle className="h-4 w-4 shrink-0" />
              )}
              {feedback.message}
            </div>
          )}

          <Button type="submit" disabled={isUpdating} className="self-start">
            {isUpdating ? "Updating..." : "Update Password"}
          </Button>
        </form>
      </div>
    </div>
  );
}
