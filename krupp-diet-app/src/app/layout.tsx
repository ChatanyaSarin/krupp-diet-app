// src/app/layout.tsx
import "./globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body
        className={`${inter.className} min-h-screen bg-[radial-gradient(80rem_40rem_at_70%_-10%,rgba(198,146,20,0.18),transparent),radial-gradient(90rem_60rem_at_-10%_-20%,rgba(24,43,73,0.25),transparent)] bg-uc-blue/95 text-slate-100`}
      >
        <main className="mx-auto max-w-6xl px-4 py-10">{children}</main>
      </body>
    </html>
  );
}
