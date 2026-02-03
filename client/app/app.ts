const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getHealth() {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("API error");
  return res.json();
}
