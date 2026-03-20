"use client";

import { useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface ShotPhase {
  ts?: number | null;
  knee_angle_deg?: number;
  angular_velocity_rad_s?: number;
  hold_duration?: number;
  start_ts?: number | null;
  end_ts?: number | null;
}

interface Shot {
  id: string;
  detection_window: { start: number; end: number; duration: number };
  fps: number;
  phases: Record<string, ShotPhase>;
  metrics: {
    angles: {
      elbow: { at_set_deg: number; at_load_deg: number; at_release_deg: number };
      knee: { min_during_load_deg: number; at_release_deg: number };
      hip: { at_load_deg: number; peak_extension_deg: number };
    };
    velocities: {
      peak_wrist_upward_px_s: number;
      peak_forearm_angular_velocity_rad_s: number;
      avg_ball_speed_px_frame: number | null;
    };
    release: {
      wrist_above_head_norm: number;
      wrist_above_shoulder_norm: number;
    };
    follow_through: { hold_duration_s: number };
    stability: { head_vertical_variance_norm: number };
  };
  frame_count: number;
  timing: {
    leg_drive_before_arm_extension: boolean | null;
    leg_to_elbow_delay_s: number | null;
  };
}

interface DetectResult {
  analysis?: { shots: Shot[]; video_path: string };
  feedback?: string;
  feedback_warning?: string;
  error?: string;
}

// ---------------------------------------------------------------------------
// Small helper components
// ---------------------------------------------------------------------------

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-1 border-b border-gray-100 dark:border-gray-700 last:border-0">
      <span className="text-gray-500 dark:text-gray-400 text-sm">{label}</span>
      <span className="font-medium text-sm text-gray-800 dark:text-gray-100">{value}</span>
    </div>
  );
}

function ShotCard({ shot, index }: { shot: Shot; index: number }) {
  const [open, setOpen] = useState(false);
  const m = shot.metrics;
  const dur = shot.detection_window.duration.toFixed(2);

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        <span className="font-semibold text-gray-800 dark:text-gray-100">
          Shot {index + 1}
          <span className="ml-2 text-xs font-normal text-gray-500 dark:text-gray-400">
            {dur}s · {shot.frame_count} frames · {shot.fps.toFixed(0)} fps
          </span>
        </span>
        <span className="text-gray-400">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="px-4 py-3 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Elbow */}
          <div>
            <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Elbow Angles</p>
            <MetricRow label="At set"     value={`${m.angles.elbow.at_set_deg.toFixed(1)}°`} />
            <MetricRow label="At load"    value={`${m.angles.elbow.at_load_deg.toFixed(1)}°`} />
            <MetricRow label="At release" value={`${m.angles.elbow.at_release_deg.toFixed(1)}°`} />
          </div>
          {/* Knee */}
          <div>
            <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Knee Angles</p>
            <MetricRow label="Min at load"    value={`${m.angles.knee.min_during_load_deg.toFixed(1)}°`} />
            <MetricRow label="At release"     value={`${m.angles.knee.at_release_deg.toFixed(1)}°`} />
          </div>
          {/* Release */}
          <div>
            <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Release</p>
            <MetricRow label="Wrist above head"     value={m.release.wrist_above_head_norm.toFixed(2)} />
            <MetricRow label="Wrist above shoulder" value={m.release.wrist_above_shoulder_norm.toFixed(2)} />
          </div>
          {/* Timing */}
          <div>
            <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Timing</p>
            <MetricRow
              label="Leg before arm"
              value={shot.timing.leg_drive_before_arm_extension === null ? "N/A" : shot.timing.leg_drive_before_arm_extension ? "Yes ✓" : "No"}
            />
            <MetricRow
              label="Leg → elbow delay"
              value={shot.timing.leg_to_elbow_delay_s !== null ? `${(shot.timing.leg_to_elbow_delay_s * 1000).toFixed(0)} ms` : "N/A"}
            />
            <MetricRow label="Follow-through hold" value={`${(m.follow_through.hold_duration_s * 1000).toFixed(0)} ms`} />
          </div>
          {/* Stability */}
          <div>
            <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Stability</p>
            <MetricRow label="Head variance (norm)" value={m.stability.head_vertical_variance_norm.toFixed(4)} />
          </div>
          {/* Speed */}
          <div>
            <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Speed</p>
            <MetricRow label="Peak wrist speed (px/s)" value={m.velocities.peak_wrist_upward_px_s.toFixed(1)} />
            {m.velocities.avg_ball_speed_px_frame !== null && (
              <MetricRow label="Avg ball speed (px/frame)" value={m.velocities.avg_ball_speed_px_frame.toFixed(1)} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/** Parse LLM feedback text into labelled sections (splits on markdown ##/### headers). */
function parseFeedbackSections(text: string): { heading: string; body: string }[] {
  const lines = text.split("\n");
  const sections: { heading: string; body: string }[] = [];
  let current: { heading: string; lines: string[] } | null = null;

  for (const line of lines) {
    const headingMatch = line.match(/^#{1,3}\s+(.*)/);
    if (headingMatch) {
      if (current) sections.push({ heading: current.heading, body: current.lines.join("\n").trim() });
      current = { heading: headingMatch[1].trim(), lines: [] };
    } else if (current) {
      current.lines.push(line);
    } else {
      // Text before the first heading
      if (!current) current = { heading: "", lines: [] };
      current.lines.push(line);
    }
  }
  if (current) sections.push({ heading: current.heading, body: current.lines.join("\n").trim() });
  return sections.filter((s) => s.body.trim() || s.heading);
}

function FeedbackPanel({ text }: { text: string }) {
  const sections = parseFeedbackSections(text);

  // If there are no markdown headings, just render as paragraphs
  if (sections.length === 1 && !sections[0].heading) {
    return (
      <div className="prose prose-sm dark:prose-invert max-w-none space-y-2">
        {sections[0].body.split("\n").filter(Boolean).map((p, i) => (
          <p key={i} className="text-gray-700 dark:text-gray-300 leading-relaxed">{p}</p>
        ))}
      </div>
    );
  }

  const sectionColors: Record<string, string> = {
    "overall": "blue",
    "strength": "green",
    "improve": "amber",
    "recommend": "purple",
    "priorit": "purple",
  };

  function colorFor(heading: string) {
    const h = heading.toLowerCase();
    for (const [key, color] of Object.entries(sectionColors)) {
      if (h.includes(key)) return color;
    }
    return "gray";
  }

  const colorClasses: Record<string, string> = {
    blue:   "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700",
    green:  "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700",
    amber:  "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-700",
    purple: "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-700",
    gray:   "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700",
  };

  const headingColors: Record<string, string> = {
    blue:   "text-blue-700 dark:text-blue-300",
    green:  "text-green-700 dark:text-green-300",
    amber:  "text-amber-700 dark:text-amber-300",
    purple: "text-purple-700 dark:text-purple-300",
    gray:   "text-gray-700 dark:text-gray-300",
  };

  return (
    <div className="space-y-3">
      {sections.map((sec, i) => {
        const color = colorFor(sec.heading);
        return (
          <div key={i} className={`rounded-lg border p-4 ${colorClasses[color]}`}>
            {sec.heading && (
              <h4 className={`font-semibold mb-2 ${headingColors[color]}`}>{sec.heading}</h4>
            )}
            <div className="space-y-1">
              {sec.body.split("\n").filter(Boolean).map((line, j) => {
                // Render bullet points nicely
                const bulletMatch = line.match(/^[-*•]\s+(.*)/);
                const numberedMatch = line.match(/^\d+\.\s+(.*)/);
                if (bulletMatch) {
                  return (
                    <div key={j} className="flex gap-2 text-sm text-gray-700 dark:text-gray-300">
                      <span className="mt-1 flex-shrink-0">•</span>
                      <span className="leading-relaxed">{bulletMatch[1]}</span>
                    </div>
                  );
                }
                if (numberedMatch) {
                  return (
                    <div key={j} className="flex gap-2 text-sm text-gray-700 dark:text-gray-300">
                      <span className="mt-1 flex-shrink-0 font-medium">{j + 1}.</span>
                      <span className="leading-relaxed">{numberedMatch[1]}</span>
                    </div>
                  );
                }
                return (
                  <p key={j} className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {line}
                  </p>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function DetectPage() {
  const [video, setVideo] = useState<File | null>(null);
  const [result, setResult] = useState<DetectResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setVideo(e.target.files[0]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!video) return;
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("video", video);

    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    try {
      const res = await fetch(`${baseUrl}/detect`, { method: "POST", body: formData });
      const data: DetectResult = await res.json();
      setResult(data);
    } catch (err: unknown) {
      setResult({ error: err instanceof Error ? err.message : String(err) });
    } finally {
      setLoading(false);
    }
  };

  const shots = result?.analysis?.shots ?? [];

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black py-10 px-4">
      <div className="mx-auto w-full max-w-2xl space-y-6">

        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AirBall</h1>
          <p className="mt-1 text-gray-500 dark:text-gray-400 text-sm">Upload a clip to analyse your shot</p>
        </div>

        {/* Upload card */}
        <div className="bg-white dark:bg-gray-900 shadow rounded-xl p-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <label className="block">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Video file</span>
              <input
                className="mt-1 block w-full text-sm text-gray-700 dark:text-gray-300
                           file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0
                           file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700
                           hover:file:bg-blue-100 dark:file:bg-blue-900/30 dark:file:text-blue-300
                           cursor-pointer"
                type="file"
                accept="video/*"
                onChange={handleFileChange}
              />
            </label>
            <button
              type="submit"
              disabled={loading || !video}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50
                         text-white font-semibold rounded-lg transition-colors"
            >
              {loading ? "Analysing…" : "Analyse Shot"}
            </button>
          </form>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex justify-center items-center gap-3 py-6 text-gray-500 dark:text-gray-400">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Processing video…
          </div>
        )}

        {/* Error */}
        {result?.error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl p-4">
            <p className="text-red-700 dark:text-red-300 font-semibold">Error</p>
            <p className="text-red-600 dark:text-red-400 text-sm mt-1">{result.error}</p>
          </div>
        )}

        {/* Results */}
        {result && !result.error && (
          <>
            {/* Shot summaries */}
            {shots.length > 0 && (
              <div className="bg-white dark:bg-gray-900 shadow rounded-xl p-6 space-y-3">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
                  {shots.length} Shot{shots.length !== 1 ? "s" : ""} Detected
                </h2>
                {shots.map((shot, i) => (
                  <ShotCard key={shot.id} shot={shot} index={i} />
                ))}
              </div>
            )}

            {shots.length === 0 && (
              <div className="bg-white dark:bg-gray-900 shadow rounded-xl p-6 text-center text-gray-500 dark:text-gray-400">
                No shots detected in this clip.
              </div>
            )}

            {/* LLM Feedback */}
            {result.feedback && (
              <div className="bg-white dark:bg-gray-900 shadow rounded-xl p-6">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">
                  Coaching Feedback
                </h2>
                <FeedbackPanel text={result.feedback} />
              </div>
            )}

            {/* Feedback warning */}
            {result.feedback_warning && (
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-xl p-4 text-sm text-amber-700 dark:text-amber-300">
                {result.feedback_warning}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}