export const API_BASE_URL = "http://localhost:8000";

export const API_ENDPOINTS = {
  signup: `${API_BASE_URL}/auth/signup`,
  login: `${API_BASE_URL}/auth/login`,
  getCurrentUser: `${API_BASE_URL}/auth/me`,
  forgotPassword: `${API_BASE_URL}/auth/forgot-password`,
  uploadVideo: `${API_BASE_URL}/upload/video`,
};

export async function apiCall<T>(
  url: string,
  options?: RequestInit,
): Promise<{ ok: boolean; data?: T; error?: string }> {
  try {
    const isFormData = options?.body instanceof FormData;

    const response = await fetch(url, {
      ...options,
      headers: {
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        ...options?.headers,
      },
    });

    const contentType = response.headers.get("content-type");

    if (!response.ok) {
      let errorMessage = "An error occurred";

      if (contentType?.includes("application/json")) {
        const data = await response.json();
        errorMessage = data.detail || data.error || "An error occurred";
      } else {
        errorMessage = await response.text();
      }

      return {
        ok: false,
        error: errorMessage,
      };
    }

    if (contentType?.includes("application/json")) {
      const data = await response.json();
      return { ok: true, data };
    }

    return { ok: true, data: undefined };
  } catch {
    return {
      ok: false,
      error: "An error occurred. Please check if the backend is running.",
    };
  }
}