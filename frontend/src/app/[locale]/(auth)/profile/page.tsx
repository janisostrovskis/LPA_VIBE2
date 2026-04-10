"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/lib/auth-context";
import { updateMe, exportMyData, type ApiError } from "@/lib/api-client";
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

export default function ProfilePage() {
  const t = useTranslations("auth");
  const { user, token, refreshUser } = useAuth();

  const [displayName, setDisplayName] = useState(user?.display_name ?? "");
  const [preferredLocale, setPreferredLocale] = useState(
    user?.preferred_locale ?? "lv",
  );
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  async function handleSave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token) return;

    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);

    try {
      await updateMe(token, {
        display_name: displayName,
        preferred_locale: preferredLocale,
      });
      await refreshUser();
      setSaveSuccess(true);
    } catch (err: unknown) {
      const detail = isApiError(err)
        ? err.detail
        : String(err);
      setSaveError(detail);
    } finally {
      setSaving(false);
    }
  }

  async function handleExport() {
    if (!token) return;

    setExporting(true);
    setExportError(null);

    try {
      const data = await exportMyData(token);
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "lpa-my-data.json";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      const detail = isApiError(err)
        ? err.detail
        : String(err);
      setExportError(detail);
    } finally {
      setExporting(false);
    }
  }

  return (
    <main className="max-w-xl mx-auto px-lpa-m py-lpa-xl">
      <h1 className="font-display text-display-md text-lpa-on-surface mb-lpa-l">
        {t("profile")}
      </h1>

      {/* Read-only info */}
      <Card className="mb-lpa-m">
        <p className="font-label text-label-sm text-lpa-on-surface-variant mb-1 uppercase tracking-widest">
          {t("email")}
        </p>
        <p className="font-body text-body-lg text-lpa-on-surface">{user?.email}</p>
      </Card>

      {/* Edit form */}
      <Card>
        <h2 className="font-headline text-headline-md text-lpa-on-surface mb-lpa-m">
          {t("editProfile")}
        </h2>

        <form onSubmit={(e) => { void handleSave(e); }} noValidate>
          <div className="flex flex-col gap-lpa-m">
            <Input
              id="displayName"
              label={t("displayName")}
              value={displayName}
              onChange={(e) => {
                setDisplayName(e.target.value);
                setSaveSuccess(false);
              }}
              autoComplete="name"
            />

            <div className="flex flex-col">
              <label
                htmlFor="preferredLocale"
                className="mb-2 font-label text-label-sm text-lpa-on-surface-variant font-medium uppercase tracking-widest"
              >
                {t("locale")}
              </label>
              <select
                id="preferredLocale"
                value={preferredLocale}
                onChange={(e) => {
                  setPreferredLocale(e.target.value);
                  setSaveSuccess(false);
                }}
                className="w-full bg-transparent border-0 border-b border-lpa-outline-variant/40 py-3 font-body text-body-md text-lpa-on-surface focus-visible:outline-none focus-visible:border-b-2 focus-visible:border-lpa-secondary"
              >
                <option value="lv">LV</option>
                <option value="en">EN</option>
                <option value="ru">RU</option>
              </select>
            </div>

            {saveError && (
              <p role="alert" className="text-lpa-error text-body-md">
                {saveError}
              </p>
            )}

            {saveSuccess && (
              <p role="status" className="text-lpa-secondary text-body-md">
                {t("saved")}
              </p>
            )}

            <Button type="submit" variant="primary" loading={saving}>
              {t("editProfile")}
            </Button>
          </div>
        </form>
      </Card>

      {/* GDPR export */}
      <div className="mt-lpa-m">
        {exportError && (
          <p role="alert" className="mb-lpa-xs text-lpa-error text-body-md">
            {exportError}
          </p>
        )}
        <Button
          variant="secondary"
          onClick={() => { void handleExport(); }}
          loading={exporting}
        >
          {t("exportData")}
        </Button>
      </div>
    </main>
  );
}
