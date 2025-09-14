"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { readUsername } from "@/lib/user";

type Section = "breakfast" | "lunch" | "dinner";
type Item = {
  description?: string;
  ingredients: Record<string, string>;
  steps?: string[] | string;
};
type IngredientsResponse = Record<Section, Record<string, Item>>;

export default function IngredientsPage() {
  const router = useRouter();
  const search = useSearchParams();

  // keep hook order stable; read client-only stuff after mount
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  const username = useMemo(() => (mounted ? readUsername(search) : null), [mounted, search]);

  const slugs = useMemo(() => {
    const split = (k: string) =>
      ((mounted ? search.get(k) : null) ?? "")
        .split(",")
        .map(s => s.trim())
        .filter(Boolean);
    return { b: split("b"), l: split("l"), d: split("d") };
  }, [mounted, search]);

  const [data, setData] = useState<IngredientsResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (mounted && !username) router.replace("/login");
  }, [mounted, username, router]);

  useEffect(() => {
    if (!mounted || !username) return;
    (async () => {
      try {
        // inside useEffect where we fetch:
        const all = [...slugs.b, ...slugs.l, ...slugs.d];
        const d = await api.chosenIngredients(username, all);
        setData(d);

      } catch (e: any) {
        setErr(String(e?.message ?? e));
      }
    })();
  }, [mounted, username, slugs]);

  // ---------- helpers ----------
  const pretty = (slug: string) =>
    slug.replace(/[-_]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());

  const normalizeSteps = (steps?: string[] | string): string[] => {
    if (!steps) return [];
    if (Array.isArray(steps)) return steps.map(s => s.trim()).filter(Boolean);
    const nl = steps.replace(/\r/g, "").split("\n").map(s => s.trim()).filter(Boolean);
    return nl.length ? nl : steps.split(".").map(s => s.trim()).filter(Boolean);
  };

  // Very pragmatic unit-aware aggregator:
  // groups by ingredient name (case-insensitive),
  // sums numeric amounts when units match; otherwise lists distinct amounts.
  type Acc = { units: Map<string, number>; extras: Set<string> };
  const aggregateShopping = (payload: IngredientsResponse | null): Record<string, string> => {
    const out: Record<string, string> = {};
    if (!payload) return out;

    const acc = new Map<string, Acc>();

    const add = (name: string, amount: string) => {
      const key = name.trim().toLowerCase();
      const a = acc.get(key) ?? { units: new Map(), extras: new Set() };

      const m = String(amount).trim().match(/^(\d+(?:\.\d+)?)\s*(.*)$/);
      if (m) {
        const qty = parseFloat(m[1]);
        const unit = (m[2] || "").trim().toLowerCase(); // e.g., "cup", "g", "tbsp", "to taste"
        if (!Number.isNaN(qty) && unit) {
          a.units.set(unit, (a.units.get(unit) ?? 0) + qty);
        } else if (!Number.isNaN(qty) && !unit) {
          a.units.set("", (a.units.get("") ?? 0) + qty);
        } else {
          a.extras.add(String(amount));
        }
      } else {
        a.extras.add(String(amount));
      }
      acc.set(key, a);
    };

    (["breakfast", "lunch", "dinner"] as Section[]).forEach(sec => {
      const section = payload[sec] || {};
      Object.values(section).forEach(item => {
        Object.entries(item.ingredients || {}).forEach(([ing, amt]) => add(ing, String(amt)));
      });
    });

    for (const [ingKey, a] of acc) {
      const unitBits = Array.from(a.units.entries())
        .map(([u, q]) => `${+q.toFixed(2)}${u ? " " + u : ""}`);
      const extraBits = Array.from(a.extras.values());
      const all = [...unitBits, ...extraBits];
      const niceName = ingKey.replace(/\b\w/g, c => c.toUpperCase());
      out[niceName] = all.join(" + ");
    }
    return out;
  };

  // ---------- UI branching ----------
  if (!mounted) return <div className="p-6">Loading…</div>;
  if (!username) return <div className="p-6">Redirecting…</div>;
  if (err) return <div className="p-6 text-red-600">{err}</div>;
  if (!data) return <div className="p-6">Loading…</div>;

  const sections: Array<[Section, string[]]> = [
    ["breakfast", slugs.b],
    ["lunch", slugs.l],
    ["dinner", slugs.d],
  ];

  const shopping = aggregateShopping(data);

  return (
    <div className="p-6 space-y-12">
      <header>
        <h1 className="text-3xl font-bold text-uc-navy">Your Recipes & Shopping List</h1>
        <p className="text-slate-600 mt-1">Ingredients and steps for today’s picks.</p>
      </header>

      {/* Recipes */}
      {sections.map(([sec, codes]) => (
        <section key={sec} className="space-y-4">
          <h2 className="text-2xl font-semibold capitalize text-uc-navy">{sec}</h2>
          {codes.length === 0 ? (
            <p className="text-slate-500">No {sec} dish selected.</p>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {codes.map((code) => {
                const item = data[sec]?.[code];
                if (!item) return null;
                const steps = normalizeSteps(item.steps);
                return (
                  <div key={code} className="card">
                    <div className="card-header">
                      <h3 className="card-title">{pretty(code)}</h3>
                      {item.description && (
                        <p className="text-sm text-slate-500">{item.description}</p>
                      )}
                    </div>
                    <div className="card-body">
                      <h4 className="font-medium text-slate-900">Ingredients</h4>
                      <ul className="mt-2 space-y-1 text-sm text-black-700">
                        {Object.entries(item.ingredients || {}).map(([ing, amt]) => (
                          <li key={ing}>
                            <span className="font-medium">{pretty(ing)}</span>: {String(amt)}
                          </li>
                        ))}
                      </ul>

                      {steps.length > 0 && (
                        <>
                          <h4 className="mt-4 font-medium text-slate-900">Steps</h4>
                          <ol className="mt-2 list-decimal list-inside space-y-1 text-sm text-black-700">
                            {steps.map((s, i) => <li key={i}>{s}</li>)}
                          </ol>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      ))}

      {/* Shopping list */}
      <section className="space-y-3">
        <h2 className="text-2xl font-semibold text-uc-navy">Shopping List</h2>
        {Object.keys(shopping).length === 0 ? (
          <p className="text-slate-500">No ingredients found.</p>
        ) : (
          <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(shopping).map(([name, amt]) => (
              <li key={name} className="rounded-xl border border-slate-200 bg-white/60 p-3 text-sm">
                <span className="font-medium">{pretty(name)}</span>: {amt}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
