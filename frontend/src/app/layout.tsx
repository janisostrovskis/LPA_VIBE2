import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Latvijas Pilates Asociācija",
  description: "LPA — Latvijas Pilates Asociācijas oficiālā mājaslapa.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="lv">
      <body>{children}</body>
    </html>
  );
}
