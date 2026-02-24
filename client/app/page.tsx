"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { uploadVideo } from "../lib/api";
import Link from "next/link";

export default function Home() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");
    if (token) {
      setIsLoggedIn(true);
      if (userData) {
        setUser(JSON.parse(userData));
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setIsLoggedIn(false);
    setUser(null);
    window.location.reload();
  };

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setMessage(null);

    if (!selectedFile) {
      setMessage("Please select a video file.");
      return;
    }

    setIsUploading(true);
    const result = await uploadVideo(selectedFile);
    setIsUploading(false);

    if (result.ok) {
      setMessage(`Upload complete. Video ID: ${result.data?.id}`);
      setSelectedFile(null);
    } else {
      setMessage(result.error || "Upload failed.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      {/* Navigation Bar */}
      {isLoggedIn && (
        <div className="fixed top-0 left-0 right-0 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 z-10">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link href="/" className="text-xl font-bold text-zinc-900 dark:text-white">
                AirBall
              </Link>
              <nav className="flex gap-4">
                <Link
                  href="/dashboard"
                  className="text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition"
                >
                  Dashboard
                </Link>
                <Link
                  href="/history"
                  className="text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition"
                >
                  History
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-zinc-600 dark:text-zinc-400">
                {user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="w-full max-w-2xl rounded-2xl bg-white p-10 shadow-sm dark:bg-zinc-950">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Upload a shot video
        </h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          Submit a video from your device and we will process it on the server.
        </p>

        {!isLoggedIn && (
          <div className="mt-4 p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 text-sm">
            <Link href="/login" className="font-medium underline">
              Login
            </Link>{" "}
            or{" "}
            <Link href="/signup" className="font-medium underline">
              sign up
            </Link>{" "}
            to track your progress and view statistics!
          </div>
        )}

        <form className="mt-8 space-y-4" onSubmit={onSubmit}>
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Video file
            </label>
            <input
              type="file"
              accept="video/*"
              className="mt-2 block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-700 shadow-sm file:mr-3 file:rounded-md file:border-0 file:bg-zinc-900 file:px-3 file:py-2 file:text-sm file:text-white hover:file:bg-zinc-800 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100"
              onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
            />
          </div>

          <button
            type="submit"
            disabled={isUploading}
            className="inline-flex items-center justify-center rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-white dark:text-black dark:hover:bg-zinc-200"
          >
            {isUploading ? "Uploading..." : "Upload video"}
          </button>
        </form>

        {message && (
          <p className="mt-4 text-sm text-zinc-700 dark:text-zinc-300">
            {message}
          </p>
        )}
      </main>
    </div>
  );
}
