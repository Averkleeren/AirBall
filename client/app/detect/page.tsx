import React, { useState } from 'react';

const DetectPage = () => {
  const [video, setVideo] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
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

    const res = await fetch('/api/detect', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div>
      <h2>Upload Video for Detection</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="video/*" onChange={handleFileChange} />
        <button type="submit" disabled={loading}>Submit</button>
      </form>
      {loading && <p>Processing...</p>}
      {result && (
        <div>
          <h3>Detection Results:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default DetectPage;