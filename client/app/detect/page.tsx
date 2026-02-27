"use client";

import { useState } from 'react';

const DetectPage = () => {
  const [video, setVideo] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null); // will contain { analysis, feedback } or error
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setVideo(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!video) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('video', video);

    // backend base url can be overridden via env var for deployment
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    try {
      const res = await fetch(`${baseUrl}/detect`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setResult({ error: err.message || String(err) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black p-4">
      <div className="w-full max-w-xl bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-semibold mb-4 text-center text-gray-800 dark:text-gray-100">
          Upload Video for Detection
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            className="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 dark:bg-gray-700 dark:border-gray-600"
            type="file"
            accept="video/*"
            onChange={handleFileChange}
          />
          <button
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded disabled:opacity-50"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Processing…' : 'Submit'}
          </button>
        </form>

        {result && (
          <div className="mt-6 text-sm">
            {result.error ? (
              <div className="text-red-600">
                <h3 className="font-semibold">Error:</h3>
                <pre className="whitespace-pre-wrap">{result.error}</pre>
              </div>
            ) : (
              <>
                <div className="mb-4">
                  <h3 className="font-semibold">Analysis:</h3>
                  <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded overflow-auto">
                    {JSON.stringify(result.analysis, null, 2)}
                  </pre>
                </div>
                <div>
                  <h3 className="font-semibold">Feedback:</h3>
                  <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded whitespace-pre-wrap">
                    {result.feedback}
                  </pre>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DetectPage;