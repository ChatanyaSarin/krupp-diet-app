"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { readUsername } from "@/lib/user";
import { DailyMealCard } from "@/components/DailyMealCard";

type Section = "breakfast" | "lunch" | "dinner";

export default function DailyPage() {
  const router = useRouter();
  const search = useSearchParams();

  // 1) Mount gate to keep SSR/CSR first render identical
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  // 2) Resolve username only after mount (can touch localStorage safely)
  const [username, setUsername] = useState<string | null>(null);
  useEffect(() => {
    if (!mounted) return;
    setUsername(readUsername(search));
  }, [mounted, search]);

  // 3) Data + selection state
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [picks, setPicks] = useState<Record<Section, string | undefined>>({
    breakfast: undefined,
    lunch: undefined,
    dinner: undefined,
  });

  // 4) Redirect only after we actually checked username on the client
  useEffect(() => {
    if (!mounted) return;
    if (username === null) return; // still resolving
    if (!username) router.replace("/login");
  }, [mounted, username, router]);

  // 5) Fetch data after username is known (and mounted)
  useEffect(() => {
    if (!mounted || !username) return;
    (async () => {
      try {
        // be resilient; even if this fails we still call /meals/daily
        try { await api.runSummaries(username, 7); } catch {}
        const d = await api.dailyMeals(username);
        setData(d);
      } catch (e: any) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, [mounted, username]);

  const allChosen = Boolean(picks.breakfast && picks.lunch && picks.dinner);

  async function submit() {
    if (!username || !data) return;
    const tasks: Promise<any>[] = [];

    (["breakfast", "lunch", "dinner"] as Section[]).forEach((sec) => {
      const chosen = picks[sec]!;
      const items = Object.keys(data[sec] ?? {});
      items.forEach((slug) => {
        tasks.push(api.feedback(username, slug, slug === chosen, /* initial */ false));
      });
    });

    await Promise.all(tasks);

    // NEW: send the chosen slugs to the ingredients page
    router.push(
  `/ingredients?b=${encodeURIComponent(picks.breakfast!)}&l=${encodeURIComponent(picks.lunch!)}&d=${encodeURIComponent(picks.dinner!)}`
  );


  }

  // ---------- Render (keep first paint stable) ----------
  if (!mounted) return <div className="p-6" />;             // same on server & client
  if (username === null) return <div className="p-6" />;    // resolving username
  if (!username) return <div className="p-6" />;            // redirecting
  if (loading) return <div className="p-6">Loading…</div>;
  if (err) return <div className="p-6 text-red-600">{err}</div>;
  if (!data) return <div className="p-6">No data.</div>;

  const sections: Section[] = ["breakfast", "lunch", "dinner"];

  return (
    <div className="space-y-10" suppressHydrationWarning>
      {sections.map((sec) => {
        const items = data[sec] ?? {};
        const slugs = Object.keys(items);
        return (
          <section key={sec}>
            <h2 className="text-2xl font-bold capitalize text-uc-navy mb-3">{sec}</h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {slugs.map((slug) => (
                <DailyMealCard
                  key={slug}
                  slug={slug}
                  title={items[slug].long_name}
                  description={items[slug].description}
                  selected={picks[sec] === slug}
                  onSelect={(s) => setPicks((p) => ({ ...p, [sec]: s }))}
                />
              ))}
            </div>
          </section>
        );
      })}

      <div className="flex justify-end">
        <button
          className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={!allChosen}
          onClick={submit}
        >
          Submit picks
        </button>
      </div>
    </div>
  );
}
