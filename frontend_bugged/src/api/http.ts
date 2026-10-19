const API_BASE = "/ap_bad";

export class ApiError extends Error {
  constructor(message: string, public status: number, public data?: unknown) {
    super(message);
    this.name = "ApiError";
  }
}

export function buildQuery(params?: Record<string, string>): string {
  if (!params || !Object.keys(params).length) return "";
  return "?" + new URLSearchParams(params).toString();
}

function getTokens() {
  return {
    access: localStorage.getItem("carevanta_access"),
    refresh: localStorage.getItem("carevanta_refresh"),
  };
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem("carevanta_access", access);
  localStorage.setItem("carevanta_refresh", refresh);
}

export function clearTokens() {
  localStorage.removeItem("carevanta_access");
  localStorage.removeItem("carevanta_refresh");
}

async function refreshAccessToken(): Promise<string | null> {
  const { refresh } = getTokens();
  if (!refresh) return null;
  const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) {
    clearTokens();
    return null;
  }
  const data = await res.json();
  localStorage.setItem("carevanta_access", data.access);
  return data.access;
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  let { access } = getTokens();
  if (access) headers.set("Authorization", `Bearer ${access}`);

  let response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 401 && getTokens().refresh) {
    access = await refreshAccessToken();
    if (access) {
      headers.set("Authorization", `Bearer ${access}`);
      response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    }
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError((data as { detail?: string }).detail || "Request failed", response.status, data);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}
