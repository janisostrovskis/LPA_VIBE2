"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/auth-context";
import { type ApiError } from "@/lib/api-client";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

function isApiError(e: unknown): e is ApiError {
  return (
    typeof e === "object" &&
    e !== null &&
    "detail" in e &&
    typeof (e as Record<string, unknown>)["detail"] === "string"
  );
}

export default function JoinPage() {
  const t = useTranslations();
  const tAuth = useTranslations("auth");
  const { register } = useAuth();
  const router = useRouter();
  const params = useParams<{ locale: string }>();
  const locale = params.locale ?? "lv";

  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{
    email?: string;
    displayName?: string;
    password?: string;
    form?: string;
  }>({});
  const [loading, setLoading] = useState(false);

  function validate(): boolean {
    const next: typeof errors = {};
    if (!email.trim()) next.email = tAuth("email") + " " + tAuth("required");
    if (!displayName.trim()) next.displayName = tAuth("displayName") + " " + tAuth("required");
    if (!password) next.password = tAuth("password") + " " + tAuth("required");
    else if (password.length < 8) next.password = tAuth("passwordTooShort");
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setErrors({});

    try {
      await register({ email, display_name: displayName, password, preferred_locale: locale });
      router.push(`/${locale}/login?registered=1`);
    } catch (err: unknown) {
      const detail = isApiError(err) ? err.detail : tAuth("registerError");
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
            {t("pages.join.title")}
          </h1>
          <p className="font-body text-body-lg text-lpa-on-surface-variant">
            {t("pages.join.subtitle")}
          </p>
        </div>

        <Card variant="feature">
          <form onSubmit={(e) => { void handleSubmit(e); }} noValidate aria-label={tAuth("register")}>
            <div className="flex flex-col gap-lpa-m">
              <Input
                id="displayName"
                label={tAuth("displayName")}
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                error={errors.displayName}
                autoComplete="name"
                aria-required="true"
              />
              <Input
                id="email"
                label={tAuth("email")}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={errors.email}
                autoComplete="email"
                aria-required="true"
              />
              <Input
                id="password"
                label={tAuth("password")}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={errors.password}
                hint={tAuth("passwordHint")}
                autoComplete="new-password"
                aria-required="true"
              />

              {errors.form && (
                <p role="alert" className="text-lpa-error text-body-md">
                  {errors.form}
                </p>
              )}

              <Button type="submit" variant="primary" loading={loading}>
                {tAuth("register")}
              </Button>
            </div>
          </form>
        </Card>

        {/* Login link */}
        <p className="mt-lpa-m text-center font-body text-body-md text-lpa-on-surface-variant">
          {tAuth("haveAccount")}{" "}
          <a
            href={`/${locale}/login`}
            className="text-lpa-secondary hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-lpa-secondary focus-visible:outline-offset-2 rounded-sm"
          >
            {tAuth("login")}
          </a>
        </p>
      </div>
    </main>
  );
}
