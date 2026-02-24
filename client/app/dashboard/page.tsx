"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUserStatistics, UserStatistics } from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<UserStatistics | null>(null);
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

    // Fetch statistics
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    setLoading(true);
    const result = await getUserStatistics();

    if (!result.ok) {
      setError(result.error || "Failed to load statistics");
      setLoading(false);
      return;
    }

    setStats(result.data || null);
    setLoading(false);
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "improving":
        return "text-green-600 dark:text-green-400";
      case "declining":
        return "text-red-600 dark:text-red-400";
      default:
        return "text-zinc-600 dark:text-zinc-400";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "improving":
        return "↗";
      case "declining":
        return "↘";
      default:
        return "→";
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-zinc-300 border-t-zinc-900 dark:border-zinc-700 dark:border-t-white"></div>
          <p className="mt-4 text-zinc-600 dark:text-zinc-400">Loading statistics...</p>
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
                Dashboard
              </h1>
              <p className="text-zinc-600 dark:text-zinc-400 mt-1">
                Welcome back, {user?.username || "Player"}!
              </p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/history"
                className="px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 text-zinc-900 dark:text-white hover:bg-zinc-100 dark:hover:bg-zinc-900 transition"
              >
                View History
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

        {stats && (
          <>
            {/* Main Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Shooting Percentage */}
              <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  Shooting Percentage
                </div>
                <div className="text-4xl font-bold text-zinc-900 dark:text-white">
                  {stats.shooting_percentage.toFixed(1)}%
                </div>
                <div className="mt-2 text-sm text-zinc-500 dark:text-zinc-500">
                  {stats.makes} makes / {stats.total_shots} attempts
                </div>
              </div>

              {/* Total Videos */}
              <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  Total Sessions
                </div>
                <div className="text-4xl font-bold text-zinc-900 dark:text-white">
                  {stats.total_videos}
                </div>
                <div className="mt-2 text-sm text-zinc-500 dark:text-zinc-500">
                  Videos processed
                </div>
              </div>

              {/* Practice Time */}
              <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  Practice Time
                </div>
                <div className="text-4xl font-bold text-zinc-900 dark:text-white">
                  {formatTime(stats.total_practice_time)}
                </div>
                <div className="mt-2 text-sm text-zinc-500 dark:text-zinc-500">
                  Total recorded
                </div>
              </div>

              {/* Average Shots Per Session */}
              <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  Shots Per Session
                </div>
                <div className="text-4xl font-bold text-zinc-900 dark:text-white">
                  {stats.average_shots_per_session.toFixed(1)}
                </div>
                <div className="mt-2 text-sm text-zinc-500 dark:text-zinc-500">
                  Average
                </div>
              </div>
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {/* Best Session */}
              <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  Best Session
                </div>
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {stats.best_session_percentage.toFixed(1)}%
                </div>
                <div className="mt-2 text-sm text-zinc-500 dark:text-zinc-500">
                  Personal best
                </div>
              </div>

              {/* Recent Trend */}
              <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  Recent Trend
                </div>
                <div className={`text-3xl font-bold flex items-center gap-2 ${getTrendColor(stats.recent_trend)}`}>
                  <span>{getTrendIcon(stats.recent_trend)}</span>
                  <span className="capitalize">{stats.recent_trend}</span>
                </div>
                <div className="mt-2 text-sm text-zinc-500 dark:text-zinc-500">
                  Last 5 vs previous 5
                </div>
              </div>

              {/* Make/Miss Breakdown */}
              <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
                <div className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                  Shot Breakdown
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-zinc-600 dark:text-zinc-400">Makes</span>
                    <span className="text-lg font-semibold text-green-600 dark:text-green-400">
                      {stats.makes}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-zinc-600 dark:text-zinc-400">Misses</span>
                    <span className="text-lg font-semibold text-red-600 dark:text-red-400">
                      {stats.misses}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Progress Visualization */}
            <div className="bg-white dark:bg-zinc-900 rounded-xl p-6 shadow-sm border border-zinc-200 dark:border-zinc-800">
              <h2 className="text-xl font-semibold text-zinc-900 dark:text-white mb-4">
                Shooting Accuracy
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-4">
                  <div className="w-24 text-sm text-zinc-600 dark:text-zinc-400">
                    Makes
                  </div>
                  <div className="flex-1 bg-zinc-200 dark:bg-zinc-800 rounded-full h-8 overflow-hidden">
                    <div
                      className="bg-green-500 h-full flex items-center justify-end pr-3 text-white text-sm font-medium transition-all duration-500"
                      style={{ width: `${stats.shooting_percentage}%` }}
                    >
                      {stats.makes}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-24 text-sm text-zinc-600 dark:text-zinc-400">
                    Misses
                  </div>
                  <div className="flex-1 bg-zinc-200 dark:bg-zinc-800 rounded-full h-8 overflow-hidden">
                    <div
                      className="bg-red-500 h-full flex items-center justify-end pr-3 text-white text-sm font-medium transition-all duration-500"
                      style={{ width: `${(stats.misses / stats.total_shots) * 100}%` }}
                    >
                      {stats.misses}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {!stats && !loading && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🏀</div>
            <h2 className="text-2xl font-semibold text-zinc-900 dark:text-white mb-2">
              No Data Yet
            </h2>
            <p className="text-zinc-600 dark:text-zinc-400 mb-6">
              Upload your first video to start tracking your progress!
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
