"use client";

import { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { saveUsername } from "@/lib/user";

export default function RegisterPage() {
  const router = useRouter();
  const qs = useSearchParams();
  const username = useMemo(() => qs.get("username") ?? "", [qs]);

  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      await api.register(username, password); // writes PasswordHash to the sheet
      saveUsername(username);
      const st = await api.status(username);
      if (!st.has_profile) {
        router.push(`/setup?username=${encodeURIComponent(username)}`);
      } else if (!st.has_initial_feedback) {
        router.push(`/initial?username=${encodeURIComponent(username)}`);
      } else {
        router.push(`/gate?username=${encodeURIComponent(username)}`);
      }
    } catch (e: any) {
      const msg = String(e);
      if (msg.includes("404")) setErr("User not in roster.");
      else setErr("Failed to set password. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4 text-uc-navy">Set your password</h1>
      <p className="text-sm mb-4">Username: <b>{username}</b></p>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          className="w-full border rounded px-3 py-2 text-black"
          type="password"
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {err && <div className="text-red-600 text-sm">{err}</div>}
        <button className="btn btn-primary" disabled={loading || !password}>
          {loading ? "Saving…" : "Save password"}
        </button>
      </form>
    </div>
  );
}
