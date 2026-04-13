"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/auth-context";
import {
  activateAccount,
  resendActivation,
  getErrorCode,
  type ApiError,
} from "@/lib/api-client";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

function isApiError(e: unknown): e is ApiError {
  return (
    typeof e === "object" &&
    e !== null &&
    "detail" in e &&
    "status" in e
  );
}

export default function ActivatePage() {
  return (
    <Suspense>
      <ActivatePageContent />
    </Suspense>
  );
}

type ActivateState = "loading" | "success" | "error";

function ActivatePageContent() {
  const t = useTranslations("auth");
  const { loginWithToken } = useAuth();
  const router = useRouter();
  const params = useParams<{ locale: string }>();
  const searchParams = useSearchParams();
  const locale = params.locale ?? "lv";

  const token = searchParams.get("token") ?? "";
  const emailFromQuery = searchParams.get("email") ?? "";

  const [state, setState] = useState<ActivateState>("loading");
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [resendEmail, setResendEmail] = useState(emailFromQuery);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const [resendError, setResendError] = useState<string | null>(null);
  const [resendCooldownUntil, setResendCooldownUntil] = useState(0);

  useEffect(() => {
    if (!token) {
      setState("error");
      setErrorCode(null);
      return;
    }

    activateAccount(token)
      .then(async ({ access_token }) => {
        setState("success");
        await loginWithToken(access_token);
        router.push(`/${locale}/profile`);
      })
      .catch((err: unknown) => {
        setState("error");
        if (isApiError(err)) {
          setErrorCode(getErrorCode(err));
        }
      });
    // Run only once on mount — token and locale are URL-derived and stable
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleResend() {
    if (!resendEmail.trim()) return;
    if (Date.now() < resendCooldownUntil) return;
    setResendLoading(true);
    setResendError(null);
    setResendSuccess(false);
    try {
      await resendActivation(resendEmail.trim());
      setResendSuccess(true);
      setResendCooldownUntil(Date.now() + 30_000);
    } catch {
      // resend-activation always returns 204 per spec (enumeration-safe);
      // any error here is a network/server fault — still show success to user
      // to preserve enumeration-safety, but log to console for diagnostics.
      // FAIL-QUIET-EXCEPTION: enumeration safety requires not revealing
      // whether email exists; network errors are surfaced via the error state.
      setResendError(t("resendError"));
    } finally {
      setResendLoading(false);
    }
  }

  if (state === "loading") {
    return (
      <main className="min-h-[80vh] flex items-center justify-center px-lpa-m py-lpa-xl">
        <div className="w-full max-w-md text-center" role="status" aria-live="polite">
          <div
            aria-hidden="true"
            className="mx-auto mb-lpa-m h-10 w-10 rounded-full border-2 border-lpa-secondary border-t-transparent animate-spin"
          />
          <p className="font-body text-body-lg text-lpa-on-surface-variant">
            {t("activating")}
          </p>
        </div>
      </main>
    );
  }

  if (state === "success") {
    // Transitioning to profile — show a brief success indicator
    return (
      <main className="min-h-[80vh] flex items-center justify-center px-lpa-m py-lpa-xl">
        <div className="w-full max-w-md text-center" role="status" aria-live="polite">
          <p className="font-body text-body-lg text-lpa-secondary">
            {t("activationSuccess")}
          </p>
        </div>
      </main>
    );
  }

  // Error state
  const isTokenInvalid = errorCode === "activation_token_invalid";

  return (
    <main className="min-h-[80vh] flex items-center justify-center px-lpa-m py-lpa-xl">
      <div className="w-full max-w-md">
        <Card variant="feature">
          <div className="flex flex-col gap-lpa-m">
            <div
              role="alert"
              className="p-lpa-s bg-lpa-error-container/20 rounded-lg border border-lpa-error/20"
            >
              <p className="font-body text-body-md text-lpa-on-surface">
                {isTokenInvalid ? t("activationTokenInvalid") : t("activationFailed")}
              </p>
            </div>

            <div className="flex flex-col gap-lpa-xs sm:flex-row">
              <Button
                type="button"
                variant="secondary"
                onClick={() => router.push(`/${locale}/login`)}
              >
                {t("goToLogin")}
              </Button>
            </div>

            {/* Resend section */}
            <div className="border-t border-lpa-outline-variant pt-lpa-m flex flex-col gap-lpa-s">
              <p className="font-body text-body-md text-lpa-on-surface-variant">
                {t("resendActivationPrompt")}
              </p>
              {resendSuccess ? (
                <p role="status" className="font-body text-body-md text-lpa-secondary">
                  {t("resendSuccess")}
                </p>
              ) : (
                <>
                  <Input
                    id="resend-email"
                    label={t("email")}
                    type="email"
                    value={resendEmail}
                    onChange={(e) => setResendEmail(e.target.value)}
                    autoComplete="email"
                    aria-required="true"
                  />
                  {resendError && (
                    <p role="alert" className="text-lpa-error text-body-sm">
                      {resendError}
                    </p>
                  )}
                  <Button
                    type="button"
                    variant="primary"
                    loading={resendLoading}
                    onClick={() => { void handleResend(); }}
                  >
                    {t("resendActivation")}
                  </Button>
                </>
              )}
            </div>
          </div>
        </Card>
      </div>
    </main>
  );
}
