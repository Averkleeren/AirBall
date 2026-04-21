import { createClient } from "@/lib/supabase/server"
import { NextResponse } from "next/server"

export async function POST(request: Request) {
  const supabase = await createClient()
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }

  try {
    const formData = await request.formData()
    const file = formData.get("video") as File

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 })
    }

    const allowedTypes = ["video/mp4", "video/quicktime", "video/webm"]
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: "Invalid file type. Please upload MP4, MOV, or WebM." },
        { status: 400 }
      )
    }

    const maxSize = 100 * 1024 * 1024 // 100MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: "File too large. Maximum size is 100MB." },
        { status: 400 }
      )
    }

    const fileExt = file.name.split(".").pop()
    const fileName = `${user.id}/${Date.now()}.${fileExt}`

    const { error: uploadError } = await supabase.storage
      .from("videos")
      .upload(fileName, file, {
        cacheControl: "3600",
        upsert: false,
      })

    if (uploadError) {
      return NextResponse.json(
        { error: "Failed to upload video" },
        { status: 500 }
      )
    }

    const {
      data: { publicUrl },
    } = supabase.storage.from("videos").getPublicUrl(fileName)

     // Simulate AI analysis with random but realistic stats
    const shotScore = Math.floor(Math.random() * 40) + 60
    const arcAngle = parseFloat((Math.random() * 15 + 38).toFixed(1))
    const releaseSpeed = parseFloat((Math.random() * 5 + 18).toFixed(1))
    const followThroughScore = Math.floor(Math.random() * 30) + 70

    const { data: video, error: dbError } = await supabase
      .from("videos")
      .insert({
        user_id: user.id,
        file_name: file.name,
        file_url: publicUrl,
        status: "analyzed",
        shot_score: shotScore,
        arc_angle: arcAngle,
        release_speed: releaseSpeed,
        follow_through_score: followThroughScore,
      })
      .select()
      .single()

    if (dbError) {
      return NextResponse.json(
        { error: "Failed to save video data" },
        { status: 500 }
      )
    }

    return NextResponse.json({ video })
    
  } catch {
    return NextResponse.json(
      { error: "Something went wrong" },
      { status: 500 }
    )
}
}