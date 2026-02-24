// API configuration and utility functions

export const API_BASE_URL = "http://localhost:8000";

export const API_ENDPOINTS = {
  signup: `${API_BASE_URL}/auth/signup`,
  login: `${API_BASE_URL}/auth/login`,
  getCurrentUser: `${API_BASE_URL}/auth/me`,
  uploadVideo: `${API_BASE_URL}/videos/upload`,
  userStatistics: `${API_BASE_URL}/statistics/me`,
  userHistory: `${API_BASE_URL}/statistics/history`,
};

export async function apiCall<T>(
  url: string,
  options?: RequestInit,
): Promise<{ ok: boolean; data?: T; error?: string }> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const data = await response.json();
      return {
        ok: false,
        error: data.detail || "An error occurred",
      };
    }

    const data = await response.json();
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      error: "An error occurred. Please check if the backend is running.",
    };
  }
}

export async function uploadVideo(
  file: File,
): Promise<{ ok: boolean; data?: { id: string; filename: string; status: string }; error?: string }> {
  try {
    const formData = new FormData();
    formData.append("file", file);

    // Get token from localStorage if available
    const token = localStorage.getItem("access_token");
    const headers: HeadersInit = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(API_ENDPOINTS.uploadVideo, {
      method: "POST",
      body: formData,
      headers,
    });

    if (!response.ok) {
      const data = await response.json();
      return {
        ok: false,
        error: data.detail || "Upload failed",
      };
    }

    const data = await response.json();
    return { ok: true, data };
  } catch (err) {
    return {
      ok: false,
      error: "Upload failed. Please check if the backend is running.",
    };
  }
}

export interface UserStatistics {
  total_videos: number;
  total_shots: number;
  makes: number;
  misses: number;
  shooting_percentage: number;
  total_practice_time: number;
  average_shots_per_session: number;
  best_session_percentage: number;
  recent_trend: string;
}

export interface VideoHistory {
  id: number;
  video_id: string;
  filename: string;
  created_at: string;
  processed_at: string | null;
  shots_detected: number;
  makes: number;
  misses: number;
  shooting_percentage: number;
  duration_seconds: number | null;
}

export async function getUserStatistics(): Promise<{
  ok: boolean;
  data?: UserStatistics;
  error?: string;
}> {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return { ok: false, error: "Not authenticated" };
  }

  return apiCall<UserStatistics>(API_ENDPOINTS.userStatistics, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

export async function getUserHistory(): Promise<{
  ok: boolean;
  data?: VideoHistory[];
  error?: string;
}> {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return { ok: false, error: "Not authenticated" };
  }

  return apiCall<VideoHistory[]>(API_ENDPOINTS.userHistory, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

