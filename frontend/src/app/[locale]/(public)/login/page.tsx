"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/auth-context";
import { requestMagicLink, type ApiError } from "@/lib/api-client";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

type Mode = "password" | "magic";

function isApiError(e: unknown): e is ApiError {
  return (
    typeof e === "object" &&
    e !== null &&
    "detail" in e &&
    typeof (e as Record<string, unknown>)["detail"] === "string"
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginPageContent />
    </Suspense>
  );
}

function LoginPageContent() {
  const t = useTranslations("auth");
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const params = useParams<{ locale: string }>();
  const searchParams = useSearchParams();
  const locale = params.locale ?? "lv";

  const [mode, setMode] = useState<Mode>("password");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string; form?: string }>({});
  const [loading, setLoading] = useState(false);
  const [magicSent, setMagicSent] = useState(false);
  const registerSuccess = searchParams.get("registered") === "1";

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.replace(`/${locale}/profile`);
    }
  }, [isAuthenticated, locale, router]);

  function validate(): boolean {
    const next: typeof errors = {};
    if (!email.trim()) next.email = t("email") + " " + t("required");
    if (mode === "password" && !password) next.password = t("password") + " " + t("required");
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handlePasswordLogin(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setErrors({});

    try {
      await login(email, password);
      router.push(`/${locale}/profile`);
    } catch (err: unknown) {
      const detail = isApiError(err) ? err.detail : t("invalidCredentials");
      setErrors({ form: detail });
    } finally {
      setLoading(false);
    }
  }

  async function handleMagicLink(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!email.trim()) {
      setErrors({ email: t("email") + " " + t("required") });
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      await requestMagicLink(email);
      setMagicSent(true);
    } catch (err: unknown) {
      const detail = isApiError(err) ? err.detail : t("invalidCredentials");
      setErrors({ form: detail });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-[80vh] flex items-center justify-center px-lpa-m py-lpa-xl">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-lpa-l text-center">
          <h1 className="font-display text-display-md text-lpa-on-surface mb-lpa-xs">
            {t("login")}
          </h1>
          <p className="font-body text-body-lg text-lpa-on-surface-variant">
            {t("loginSubtitle")}
          </p>
        </div>

        <Card variant="feature">
          {/* Register success message */}
          {registerSuccess && (
            <div
              role="status"
              className="mb-lpa-m p-lpa-s bg-lpa-secondary-container/30 rounded-lg"
            >
              <p className="font-body text-body-md text-lpa-on-secondary-container">
                {t("registerSuccess")}
              </p>
            </div>
          )}

          {/* Mode switcher */}
          <div className="flex gap-lpa-xs mb-lpa-l" role="tablist">
            <button
              role="tab"
              aria-selected={mode === "password"}
              onClick={() => {
                setMode("password");
                setErrors({});
                setMagicSent(false);
              }}
              className={[
                "flex-1 py-2 font-label text-label-md rounded-pill transition-all duration-200",
                mode === "password"
                  ? "bg-lpa-secondary text-lpa-on-secondary"
                  : "text-lpa-on-surface-variant hover:text-lpa-on-surface",
              ].join(" ")}
            >
              {t("login")}
            </button>
            <button
              role="tab"
              aria-selected={mode === "magic"}
              onClick={() => {
                setMode("magic");
                setErrors({});
                setMagicSent(false);
              }}
              className={[
                "flex-1 py-2 font-label text-label-md rounded-pill transition-all duration-200",
                mode === "magic"
                  ? "bg-lpa-secondary text-lpa-on-secondary"
                  : "text-lpa-on-surface-variant hover:text-lpa-on-surface",
              ].join(" ")}
            >
              {t("magicLink")}
            </button>
          </div>

          {/* Password form */}
          {mode === "password" && (
            <form onSubmit={(e) => { void handlePasswordLogin(e); }} noValidate>
              <div className="flex flex-col gap-lpa-m">
                <Input
                  id="email"
                  label={t("email")}
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={errors.email}
                  autoComplete="email"
                  aria-required="true"
                />
                <Input
                  id="password"
                  label={t("password")}
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  error={errors.password}
                  autoComplete="current-password"
                  aria-required="true"
                />

                {errors.form && (
                  <p role="alert" className="text-lpa-error text-body-md">
                    {errors.form}
                  </p>
                )}

                <Button type="submit" variant="primary" loading={loading}>
                  {t("login")}
                </Button>
              </div>
            </form>
          )}

          {/* Magic link form */}
          {mode === "magic" && !magicSent && (
            <form onSubmit={(e) => { void handleMagicLink(e); }} noValidate>
              <div className="flex flex-col gap-lpa-m">
                <Input
                  id="magic-email"
                  label={t("email")}
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={errors.email}
                  autoComplete="email"
                  aria-required="true"
                />

                {errors.form && (
                  <p role="alert" className="text-lpa-error text-body-md">
                    {errors.form}
                  </p>
                )}

                <Button type="submit" variant="primary" loading={loading}>
                  {t("magicLink")}
                </Button>
              </div>
            </form>
          )}

          {/* Magic link sent confirmation */}
          {mode === "magic" && magicSent && (
            <div role="status" className="text-center py-lpa-m">
              <p className="font-body text-body-lg text-lpa-on-surface mb-lpa-xs">
                {t("magicLinkSent")}
              </p>
              <p className="font-body text-body-md text-lpa-on-surface-variant">
                {email}
              </p>
            </div>
          )}
        </Card>

        {/* Register link */}
        <p className="mt-lpa-m text-center font-body text-body-md text-lpa-on-surface-variant">
          {t("noAccount")}{" "}
          <a
            href={`/${locale}/join`}
            className="text-lpa-secondary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm"
          >
            {t("register")}
          </a>
        </p>
      </div>
    </main>
  );
}
