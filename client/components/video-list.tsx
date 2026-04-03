"use client"

import { createClient } from "@/lib/supabase/client"
import useSWR from "swr"

interface Video {
  id: string
  file_name: string
  file_url: string
  status: string
  shot_score: number | null
  arc_angle: number | null
  release_speed: number | null
  follow_through_score: number | null
  created_at: string
}

async function fetchVideos(): Promise<Video[]> {
  const supabase = createClient()
  const { data, error } = await supabase
    .from("videos")
    .select("*")
    .order("created_at", { ascending: false })

  if (error) throw error
  return data ?? []
}

function StatBlock({ label, value, unit }: { label: string; value: string | number | null; unit?: string }) {
  return (
    <div className="text-center">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-bold text-foreground tabular-nums">
        {value ?? "--"}
        {unit && <span className="text-xs font-normal text-muted-foreground">{unit}</span>}
      </p>
    </div>
  )
}

export function VideoList() {
  const { data: videos, error, isLoading } = useSWR("videos", fetchVideos)

  if (isLoading) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">
        Loading your shots...
      </div>
    )
  }

  if (error) {
    return (
      <div className="py-12 text-center text-sm text-destructive">
        Failed to load videos. Please refresh the page.
      </div>
    )
  }

  if (!videos || videos.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-sm text-muted-foreground">
          No videos yet. Upload your first shot to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {videos.map((video) => (
        <div
          key={video.id}
          className="rounded-xl border border-border bg-card p-6"
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0 flex-1">
              <h3 className="truncate text-sm font-semibold text-card-foreground">
                {video.file_name}
              </h3>
              <p className="mt-1 text-xs text-muted-foreground">
                {new Date(video.created_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                  hour: "numeric",
                  minute: "2-digit",
                })}
              </p>
            </div>

            {video.status === "analyzed" && (
              <div className="flex gap-6">
                <StatBlock label="Shot Score" value={video.shot_score} />
                <StatBlock label="Arc" value={video.arc_angle} unit="deg" />
                <StatBlock label="Speed" value={video.release_speed} unit="mph" />
                <StatBlock label="Follow-Through" value={video.follow_through_score} />
              </div>
            )}

            {video.status === "processing" && (
              <span className="inline-flex items-center rounded-md bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">
                Processing...
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}