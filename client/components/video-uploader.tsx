"use client"

import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { useCallback, useRef, useState } from "react"
import { mutate } from "swr"

export function VideoUploader({ userId }: { userId: string }) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.type.startsWith("video/")) {
        setUploadError("Please upload a video file")
        return
      }

      if (file.size > 100 * 1024 * 1024) {
        setUploadError("File must be under 100 MB")
        return
      }

      setIsUploading(true)
      setUploadError(null)

      const supabase = createClient()
      const fileExt = file.name.split(".").pop()
      const filePath = `${userId}/${Date.now()}.${fileExt}`

      const { error: storageError } = await supabase.storage
        .from("videos")
        .upload(filePath, file)

      if (storageError) {
        setUploadError("Upload failed. Please try again.")
        setIsUploading(false)
        return
      }

      const {
        data: { publicUrl },
      } = supabase.storage.from("videos").getPublicUrl(filePath)

      // Generate random stats (simulating AI analysis)
      const shotScore = Math.floor(Math.random() * 40) + 60
      const arcAngle = Math.floor(Math.random() * 20) + 40
      const releaseSpeed = +(Math.random() * 5 + 18).toFixed(1)
      const followThroughScore = Math.floor(Math.random() * 30) + 70

      const { error: dbError } = await supabase.from("videos").insert({
        user_id: userId,
        file_name: file.name,
        file_url: publicUrl,
        status: "analyzed",
        shot_score: shotScore,
        arc_angle: arcAngle,
        release_speed: releaseSpeed,
        follow_through_score: followThroughScore,
      })

      if (dbError) {
        setUploadError("Failed to save analysis. Please try again.")
        setIsUploading(false)
        return
      }

      setIsUploading(false)
      mutate("videos")
    },
    [userId]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleUpload(file)
    },
    [handleUpload]
  )

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleUpload(file)
    },
    [handleUpload]
  )

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 text-center transition-colors ${
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/40"
        }`}
      >
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-6 w-6 text-primary"
            aria-hidden="true"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>

        {isUploading ? (
          <p className="text-sm font-medium text-foreground">
            Uploading & analyzing...
          </p>
        ) : (
          <>
            <p className="text-sm font-medium text-foreground">
              Drag and drop your video here
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              or click below to browse. Max 100 MB.
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={() => fileInputRef.current?.click()}
            >
              Choose file
            </Button>
          </>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          className="sr-only"
          onChange={handleFileChange}
          aria-label="Upload video file"
        />
      </div>

      {uploadError && (
        <p className="mt-3 text-center text-sm text-destructive">
          {uploadError}
        </p>
      )}
    </div>
  )
}
