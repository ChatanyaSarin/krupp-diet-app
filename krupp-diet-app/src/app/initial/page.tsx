"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { readUsername } from "@/lib/user";
import { MealCard } from "@/components/MealCard"; // ensure this import exists

type MealMeta = {
  long_name: string;
  description?: string;
  ingredients: Record<string, string>;
  instructions: string;
};

export default function InitialPage() {
  const router = useRouter();
  const search = useSearchParams();

  // Prevent hydration mismatches: don't read URL/localStorage until mounted
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const username = useMemo(
    () => (mounted ? readUsername(search) : ""),
    [mounted, search]
  );

  const [meals, setMeals] = useState<Record<string, MealMeta>>({});
  const [decisions, setDecisions] = useState<Record<string, boolean>>({});
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch initial suggestions once we know the username on the client
  useEffect(() => {
    if (!mounted) return;
    if (!username) {
      router.replace("/login");
      return;
    }
    setLoading(true);
    setErr(null);
    api
      .initialMeals(username)
      .then((data) => setMeals(data || {}))
      .catch((e) => setErr(String(e)))
      .finally(() => setLoading(false));
  }, [mounted, username, router]);

  if (!mounted) return null; // first paint matches on server/client

  if (!username) return null; // redirecting

  if (err) return <div className="p-6 text-red-600">Error: {err}</div>;

  if (loading) return <div className="p-6">Loading…</div>;

  const keys = Object.keys(meals);
  const allDecided = keys.length > 0 && keys.every((k) => k in decisions);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white">Pick your favorites</h1>
        <p className="text-slate-200">
          Make a call on{" "}
          <span className="text-uc-gold font-semibold">every meal</span> to
          continue.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {keys.map((k) => {
          const m = meals[k];
          return (
            <MealCard
              key={k}
              title={m.long_name}
              description={m.description || ""}
              onChoose={async (liked) => {
                // record locally
                setDecisions((d) => ({ ...d, [k]: liked }));
                // send to backend (uses correct signature)
                await api.feedback(username, k, liked, /* initial */ true);
              }}
            />
          );
        })}
      </div>

      <div className="mt-8 flex justify-end">
        <button
          className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!allDecided}
          onClick={() =>
            router.push(`/biomarkers?username=${encodeURIComponent(username)}`)
          }
        >
          Continue
        </button>
      </div>
    </div>
  );
}
