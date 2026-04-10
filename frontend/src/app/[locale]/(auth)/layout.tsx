"use client";

import { useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const params = useParams<{ locale: string }>();
  const locale = params.locale ?? "lv";

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace(`/${locale}/login`);
    }
  }, [isAuthenticated, isLoading, locale, router]);

  if (isLoading) {
    return (
      <div
        className="flex min-h-[60vh] items-center justify-center"
        aria-busy="true"
        aria-label="Loading"
      >
        <span className="h-8 w-8 animate-spin rounded-full border-2 border-lpa-secondary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect is in-flight; render nothing while navigating.
    return null;
  }

  return <>{children}</>;
}
