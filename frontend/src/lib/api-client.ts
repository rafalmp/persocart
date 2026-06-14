export class ApiError extends Error {
  constructor(
    public status: number,
    public data: unknown,
  ) {
    super(`HTTP ${status}`);
  }
}

function getCsrfToken(): string {
  const match = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="));
  return match ? match.split("=")[1].trim() : "";
}

export async function apiFetch<T>(
  url: string,
  init: RequestInit = {},
): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  const isWriteMethod = ["POST", "PUT", "PATCH", "DELETE"].includes(method);

  const headers = new Headers(init.headers);
  if (isWriteMethod) {
    headers.set("X-CSRFToken", getCsrfToken());
  }
  if (!(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`/api/v1${url}`, {
    ...init,
    credentials: "include",
    headers,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({ message: "Request failed" }));
    throw new ApiError(res.status, data);
  }

  if (res.status === 204) return null as T;
  return res.json() as Promise<T>;
}
