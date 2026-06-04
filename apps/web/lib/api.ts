const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T = unknown>(
  path: string,
  options?: RequestInit & { json?: unknown }
): Promise<T> {
  const { json, ...init } = options || {};
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    body: json ? JSON.stringify(json) : init?.body,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: { message: res.statusText } }));
    throw new Error(error?.error?.message || error?.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T = unknown>(path: string) => apiFetch<T>(path),
  post: <T = unknown>(path: string, data?: unknown) => apiFetch<T>(path, { method: "POST", json: data }),
  put: <T = unknown>(path: string, data?: unknown) => apiFetch<T>(path, { method: "PUT", json: data }),
  delete: <T = unknown>(path: string) => apiFetch<T>(path, { method: "DELETE" }),
  uploadFile: async <T = unknown>(path: string, file: File): Promise<T> => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}${path}`, { method: "POST", body: formData });
    if (!res.ok) {
      const error = await res.json().catch(() => null);
      const message = error?.detail || error?.message || `Upload failed (HTTP ${res.status})`;
      throw new Error(message);
    }
    return res.json();
  },
};
