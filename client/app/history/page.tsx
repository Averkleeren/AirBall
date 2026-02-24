"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUserHistory, VideoHistory } from "@/lib/api";
import Link from "next/link";

export default function HistoryPage() {
  const router = useRouter();
  const [history, setHistory] = useState<VideoHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");

    if (!token) {
      router.push("/login");
      return;
    }

    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Fetch history
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    const result = await getUserHistory();

    if (!result.ok) {
      setError(result.error || "Failed to load history");
      setLoading(false);
      return;
    }

    setHistory(result.data || []);
    setLoading(false);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return "N/A";
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, "0")}`;
  };

  const getPercentageColor = (percentage: number) => {
    if (percentage >= 70) return "text-green-600 dark:text-green-400";
    if (percentage >= 50) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-white"></div>
          <p className="mt-4 text-zinc-600 dark:text-zinc-400">Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                Session History
              </h1>
              <p className="text-zinc-600 dark:text-zinc-400 mt-1">
                View all your practice sessions and performance
              </p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/dashboard"
                className="px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-white hover:bg-zinc-100 dark:hover:bg-zinc-900 transition"
              >
                Dashboard
              </Link>
              <Link
                href="/"
                className="px-4 py-2 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-zinc-200 transition"
              >
                Upload Video
              </Link>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-300">
            {error}
          </div>
        )}

        {history.length > 0 ? (
          <div className="space-y-4">
            {history.map((video) => (
              <div
                key={video.id}
                className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 transition"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  {/* Left side - Video info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="text-3xl">🏀</div>
                      <div>
                        <h3 className="text-lg font-semibold text-zinc-900 dark:text-white">
                          {video.filename}
                        </h3>
                        <p className="text-sm text-zinc-500 dark:text-zinc-500">
                          {formatDate(video.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-4 mt-3">
                      <div className="text-sm">
                        <span className="text-zinc-600 dark:text-zinc-400">Duration:</span>
                        <span className="ml-1 font-medium text-zinc-900 dark:text-white">
                          {formatDuration(video.duration_seconds)}
                        </span>
                      </div>
                      <div className="text-sm">
                        <span className="text-zinc-600 dark:text-zinc-400">Shots:</span>
                        <span className="ml-1 font-medium text-zinc-900 dark:text-white">
                          {video.shots_detected}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Right side - Stats */}
                  <div className="flex items-center gap-6">
                    {/* Shooting % */}
                    <div className="text-center">
                      <div className={`text-3xl font-bold ${getPercentageColor(video.shooting_percentage)}`}>
                        {video.shooting_percentage.toFixed(1)}%
                      </div>
                      <div className="text-xs text-zinc-500 dark:text-zinc-500 mt-1">
                        Accuracy
                      </div>
                    </div>

                    {/* Makes/Misses */}
                    <div className="flex gap-4">
                      <div className="text-center bg-green-100 dark:bg-green-900/20 px-4 py-2 rounded-lg">
                        <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                          {video.makes}
                        </div>
                        <div className="text-xs text-green-700 dark:text-green-500 mt-1">
                          Makes
                        </div>
                      </div>
                      <div className="text-center bg-red-100 dark:bg-red-900/20 px-4 py-2 rounded-lg">
                        <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                          {video.misses}
                        </div>
                        <div className="text-xs text-red-700 dark:text-red-500 mt-1">
                          Misses
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="text-xs text-zinc-500 dark:text-zinc-500">
                      Shot Distribution
                    </div>
                  </div>
                  <div className="h-2 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full flex">
                      <div
                        className="bg-green-500 transition-all duration-500"
                        style={{ width: `${video.shooting_percentage}%` }}
                      ></div>
                      <div
                        className="bg-red-500 transition-all duration-500"
                        style={{ width: `${100 - video.shooting_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-2xl font-semibold text-zinc-900 dark:text-white mb-2">
              No Sessions Yet
            </h2>
            <p className="text-zinc-600 dark:text-zinc-400 mb-6">
              Upload your first video to start building your history!
            </p>
            <Link
              href="/"
              className="inline-block px-6 py-3 rounded-lg bg-zinc-900 dark:bg-white text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-zinc-200 transition"
            >
              Upload Video
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
