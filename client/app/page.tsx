"use client";

import { useState } from "react";
import { uploadVideo } from "../lib/api";

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

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
      <main className="w-full max-w-2xl rounded-2xl bg-white p-10 shadow-sm dark:bg-zinc-950">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Upload a shot video
        </h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          Submit a video from your device and we will process it on the server.
        </p>

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
