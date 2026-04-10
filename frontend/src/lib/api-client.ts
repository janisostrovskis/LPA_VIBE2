const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ApiError {
  detail: string;
  status: number;
}

export interface MemberDto {
  id: string;
  email: string;
  display_name: string;
  preferred_locale: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

function isApiError(value: unknown): value is { detail: string } {
  return (
    typeof value === "object" &&
    value !== null &&
    "detail" in value &&
    typeof (value as Record<string, unknown>)["detail"] === "string"
  );
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body: unknown = await res.json().catch(() => ({
      detail: res.statusText,
    }));
    const detail = isApiError(body) ? body.detail : res.statusText;
    throw { detail, status: res.status } as ApiError;
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// Auth endpoints

export function register(data: {
  email: string;
  display_name: string;
  password: string;
  preferred_locale?: string;
}): Promise<MemberDto> {
  return apiFetch<MemberDto>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function requestMagicLink(email: string): Promise<void> {
  return apiFetch<void>("/api/auth/magic-link/request", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function verifyMagicLink(token: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/magic-link/verify", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export function refreshToken(accessToken: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/refresh", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

// Member endpoints

export function getMe(accessToken: string): Promise<MemberDto> {
  return apiFetch<MemberDto>("/api/members/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function updateMe(
  accessToken: string,
  data: { display_name?: string; preferred_locale?: string },
): Promise<MemberDto> {
  return apiFetch<MemberDto>("/api/members/me", {
    method: "PATCH",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(data),
  });
}

export function exportMyData(accessToken: string): Promise<Record<string, unknown>> {
  return apiFetch<Record<string, unknown>>("/api/members/me/export", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}
