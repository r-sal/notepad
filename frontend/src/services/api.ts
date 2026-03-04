const API_BASE = "/api";

// Mutex to deduplicate concurrent refresh attempts
let refreshPromise: Promise<boolean> | null = null;

async function attemptRefresh(): Promise<boolean> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return false;

  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) return false;

    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

function buildHeaders(token: string | null, extra?: HeadersInit): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("access_token");
  const headers = buildHeaders(token, options?.headers as HeadersInit);

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // Auto-refresh on 401 (skip for auth endpoints to avoid loops)
  if (res.status === 401 && !path.startsWith("/auth/")) {
    // Deduplicate: if a refresh is already in flight, wait for it
    if (!refreshPromise) {
      refreshPromise = attemptRefresh();
    }
    const refreshed = await refreshPromise;
    refreshPromise = null;

    if (refreshed) {
      // Retry the original request with the new token
      const newToken = localStorage.getItem("access_token");
      const retryHeaders = buildHeaders(newToken, options?.headers as HeadersInit);
      const retryRes = await fetch(`${API_BASE}${path}`, { ...options, headers: retryHeaders });

      if (!retryRes.ok) {
        throw new Error(`API error: ${retryRes.status}`);
      }
      return retryRes.json() as Promise<T>;
    } else {
      // Refresh failed — session is dead, force logout
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
      throw new Error("Session expired");
    }
  }

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
