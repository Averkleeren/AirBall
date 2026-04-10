"use client"

import { createClient } from "@/lib/supabase/client"
import useSWR from "swr"
import { Video, TrendingUp, Target } from "lucide-react"

interface VideoRow {
  status: string
  shot_score: number | null
}

async function fetchStats() {
  const supabase = createClient()
  const { data, error } = await supabase
    .from("videos")
    .select("status, shot_score")

  if (error) throw error
  return data ?? []
}

export function DashboardStats() {
  const { data: videos } = useSWR<VideoRow[]>("video-stats", fetchStats)

  const totalVideos = videos?.length ?? 0
  const analyzed = videos?.filter((v) => v.status === "analyzed") ?? []
  const avgScore =
    analyzed.length > 0
      ? Math.round(
          analyzed.reduce((sum, v) => sum + (v.shot_score ?? 0), 0) /
            analyzed.filter((v) => v.shot_score !== null).length
        ) || 0
      : 0
  const bestScore =
    analyzed.length > 0
      ? Math.max(...analyzed.map((v) => v.shot_score ?? 0))
      : 0

  const stats = [
    {
      label: "Total Uploads",
      value: totalVideos,
      icon: Video,
    },
    {
      label: "Avg. Shot Score",
      value: avgScore || "—",
      icon: TrendingUp,
    },
    {
      label: "Best Score",
      value: bestScore || "—",
      icon: Target,
    },
  ]

  return (
    <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="flex items-center gap-4 rounded-xl border border-border bg-card p-5"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <stat.icon className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">{stat.label}</p>
            <p className="text-2xl font-bold tabular-nums text-foreground">
              {stat.value}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
