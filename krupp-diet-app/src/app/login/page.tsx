"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { saveUsername } from "@/lib/user";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const res = await api.login(username, password);

      // 409 from /auth/login is mapped to { needsPassword: true } by api.ts
      if ((res as any).needsPassword) {
        saveUsername(username);
        router.push(`/register?username=${encodeURIComponent(username)}`);
        return;
      }

      // ok:true → check status to decide where to go
      const st = await api.status(username);
      saveUsername(username);

      if (!st.has_profile) {
        router.push(`/setup?username=${encodeURIComponent(username)}`);
      } else if (!st.has_initial_feedback) {
        router.push(`/initial?username=${encodeURIComponent(username)}`);
      } else {
        router.push(`/gate?username=${encodeURIComponent(username)}`);
      }
    } catch (e: any) {
      const msg = String(e);
      if (msg.includes("401")) setErr("Incorrect password.");
      else if (msg.includes("404")) setErr("User not found.");
      else if (msg.includes("400")) setErr("Username required.");
      else setErr("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {/* your inputs; be sure inputs use text-black so they’re readable */}
      <input
        className="w-full border rounded px-3 py-2 text-black"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        className="w-full border rounded px-3 py-2 text-black"
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      {err && <div className="text-red-600 text-sm">{err}</div>}

      <button
        type="submit"
        className="btn btn-primary disabled:opacity-50"
        disabled={loading || !username}
      >
        {loading ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
