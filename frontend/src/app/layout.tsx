import type { Metadata } from "next";
import { Epilogue, Manrope } from "next/font/google";
import "./globals.css";

const epilogue = Epilogue({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-epilogue",
  display: "swap",
});

const manrope = Manrope({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-manrope",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Latvijas Pilates Asociacija",
  description: "LPA — Latvijas Pilates Asociacijas oficiala majaslapa.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="lv" className={`${epilogue.variable} ${manrope.variable}`}>
      <body className="font-body bg-lpa-surface text-lpa-on-surface">
        {children}
      </body>
    </html>
  );
}
