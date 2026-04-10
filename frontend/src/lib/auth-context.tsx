"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  type MemberDto,
  type TokenResponse,
  getMe,
  login as apiLogin,
  register as apiRegister,
  refreshToken as apiRefresh,
} from "@/lib/api-client";

interface AuthState {
  token: string | null;
  user: MemberDto | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  loginWithToken: (token: string) => Promise<void>;
  register: (data: {
    email: string;
    display_name: string;
    password: string;
    preferred_locale?: string;
  }) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

type AuthContextValue = AuthState & AuthActions;

const AuthContext = createContext<AuthContextValue | null>(null);

// Session-storage key for persisting the token across page reloads.
// Note: sessionStorage is cleared when the tab closes, limiting XSS exposure
// compared to localStorage while still surviving navigation.
const SESSION_KEY = "lpa_token";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<MemberDto | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const applyToken = useCallback(async (t: string) => {
    setToken(t);
    if (typeof window !== "undefined") {
      sessionStorage.setItem(SESSION_KEY, t);
    }
    const me = await getMe(t);
    setUser(me);
  }, []);

  // On mount: restore token from sessionStorage and try to refresh it.
  useEffect(() => {
    const stored =
      typeof window !== "undefined"
        ? sessionStorage.getItem(SESSION_KEY)
        : null;

    if (!stored) {
      setIsLoading(false);
      return;
    }

    apiRefresh(stored)
      .then(({ access_token }: TokenResponse) => applyToken(access_token))
      .catch(() => {
        // Stored token is invalid/expired — clear it silently.
        sessionStorage.removeItem(SESSION_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, [applyToken]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await apiLogin(email, password);
      await applyToken(access_token);
    },
    [applyToken],
  );

  const loginWithToken = useCallback(
    async (t: string) => {
      await applyToken(t);
    },
    [applyToken],
  );

  const register = useCallback(
    async (data: {
      email: string;
      display_name: string;
      password: string;
      preferred_locale?: string;
    }) => {
      await apiRegister(data);
    },
    [],
  );

  const logout = useCallback(() => {
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(SESSION_KEY);
    }
    setToken(null);
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    const me = await getMe(token);
    setUser(me);
  }, [token]);

  const value: AuthContextValue = {
    token,
    user,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    loginWithToken,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
