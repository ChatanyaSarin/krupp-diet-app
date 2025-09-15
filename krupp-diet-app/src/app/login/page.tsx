// src/app/login/page.tsx
"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api"; // or "@/lib/api" depending on your tsconfig

export default function LoginPage() {
  const router = useRouter();
  const params = useSearchParams();
  const [username, setUsername] = useState(params.get("username") ?? "");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const r = await api.login(username, password);

      // <-- YOUR ROUTING BLOCK GOES HERE -->
      if ((r as any).needsPassword) {
        router.push(`/setup?username=${encodeURIComponent(username)}`);
      } else {
        // optional: persist username for later pages
        sessionStorage.setItem("username", username);
        router.push("/gate");
      }
    } catch (e: any) {
      setErr(e?.message ?? "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen grid place-items-center">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4">
        <div>
          <label className="block text-sm font-medium">Username</label>
          <input
            className="mt-1 w-full rounded-md border text-black px-3 py-2"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
        </div>
        {err && <p className="text-sm text-red-600">{err}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-blue-900 text-white py-2 disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
