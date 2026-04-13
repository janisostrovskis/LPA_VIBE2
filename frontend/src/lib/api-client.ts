const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Structured error detail returned by backend for specific domain errors. */
export interface ApiErrorDetail {
  code: string;
  message: string;
}

export interface ApiError {
  /** Either a plain string message or a structured domain error. */
  detail: string | ApiErrorDetail;
  status: number;
}

/** Narrow an ApiError's detail to its error code, if structured. */
export function getErrorCode(err: ApiError): string | null {
  if (typeof err.detail === "object" && err.detail !== null) {
    return err.detail.code;
  }
  return null;
}

/** Narrow an ApiError's detail to a human-readable string. */
export function getErrorMessage(err: ApiError): string {
  if (typeof err.detail === "object" && err.detail !== null) {
    return err.detail.message;
  }
  return err.detail;
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

function isStructuredDetail(
  value: unknown,
): value is { code: string; message: string } {
  return (
    typeof value === "object" &&
    value !== null &&
    "code" in value &&
    "message" in value &&
    typeof (value as Record<string, unknown>)["code"] === "string" &&
    typeof (value as Record<string, unknown>)["message"] === "string"
  );
}

function parseErrorDetail(body: unknown, fallback: string): string | ApiErrorDetail {
  if (
    typeof body === "object" &&
    body !== null &&
    "detail" in body
  ) {
    const d = (body as Record<string, unknown>)["detail"];
    if (typeof d === "string") return d;
    if (isStructuredDetail(d)) return { code: d.code, message: d.message };
  }
  return fallback;
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
    const detail = parseErrorDetail(body, res.statusText);
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

export function activateAccount(token: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/api/auth/activate", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export function resendActivation(email: string): Promise<void> {
  return apiFetch<void>("/api/auth/resend-activation", {
    method: "POST",
    body: JSON.stringify({ email }),
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
