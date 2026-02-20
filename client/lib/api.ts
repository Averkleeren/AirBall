// API configuration and utility functions

export const API_BASE_URL = "http://localhost:8000";

export const API_ENDPOINTS = {
  signup: `${API_BASE_URL}/auth/signup`,
  login: `${API_BASE_URL}/auth/login`,
  getCurrentUser: `${API_BASE_URL}/auth/me`,
  uploadVideo: `${API_BASE_URL}/videos/upload`,
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

    const response = await fetch(API_ENDPOINTS.uploadVideo, {
      method: "POST",
      body: formData,
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
