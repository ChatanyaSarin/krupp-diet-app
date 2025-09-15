import { saveUsername } from "@/lib/user";
import { useRouter } from "next/navigation";

// lib/api.ts
const RAW_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";
// normalize: remove trailing slash
const API_BASE = RAW_BASE.replace(/\/+$/, "");

function u(path: string) {
  return `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
}

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    // Important for client components; avoid caching cross-origin GETs
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    // try to surface JSON error bodies
    let msg = await res.text();
    try { const j = JSON.parse(msg); msg = JSON.stringify(j); } catch {}
    throw new Error(`${res.status} ${msg}`);
  }
  // Some endpoints return no body; guard it
  const text = await res.text();
  return (text ? JSON.parse(text) : ({} as any)) as T;
}

async function handle(res: Response) {
  // let the caller check res.status before throwing
  if (!res.ok) {
    let msg: any;
    try { msg = await res.json(); } catch { msg = await res.text(); }
    const body = typeof msg === "string" ? msg : JSON.stringify(msg);
    throw new Error(`HTTP ${res.status} @ ${res.url} ${body ? `- ${body}` : ""}`);
  }
  return res.json();
}

export type OneMealIngredients = {
  description: string;
  ingredients: Record<string, string>;
  steps?: string[] | string; // backend may send an array or a single string
};

export type IngredientsSection = Record<string, OneMealIngredients>;

export type IngredientsResponse = {
  breakfast: IngredientsSection;
  lunch: IngredientsSection;
  dinner: IngredientsSection;
};


export const api = {
  login: async (usernameInput: any, passwordInput: any) => {
    // Defensive coercion in case a form object slips in
    const username =
      typeof usernameInput === "string"
        ? usernameInput.trim()
        : (usernameInput?.username ??
          usernameInput?.value ??
          usernameInput?.toString?.() ??
          "").toString().trim();

    const password = "blank";

    const res = await fetch(u("/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify({ username, password }),
    });

    // Allow the app to branch on “needsPassword” without throwing
    if (res.status === 409) return { needsPassword: true as const };
    return handle(res); // { ok: true }
  },

  register: async (usernameInput: any, passwordInput: any) => {
  // Coerce inputs (same style as login)
  const username =
    typeof usernameInput === "string"
      ? usernameInput.trim()
      : (usernameInput?.username ??
         usernameInput?.value ??
         usernameInput?.toString?.() ??
         "").toString().trim();

    const password =
      typeof passwordInput === "string"
        ? passwordInput
        : (passwordInput?.password ??
          passwordInput?.value ??
          passwordInput?.toString?.() ??
          "").toString();

    if (!username) throw new Error("Username required");
    if (!password) throw new Error("Password required");

    const res = await fetch(u("/auth/register"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify({ username, password }),
    });

    // 201 => { ok: true }
    const out = await handle(res);
    // (Optional) don’t persist here if you prefer doing it in the page:
    // try { window.localStorage.setItem("username", username); } catch {}
    return { ...out, username } as const;
  },

  async status(username: string) {
    const res = await fetch(u(`/user/status?username=${encodeURIComponent(username)}`), {
      method: "GET",
    });
    return handle(res);
  },

  setupUser(payload: {
    Username: string; Height: number; Weight: number; DietaryRestrictions: string;
  }) {
    return http<{ status: 'ok' }>('/setup_user', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  initialMeals(username: string) {
    return http<Record<string, { long_name: string; ingredients: Record<string, string>; instructions: string }>>(
      `/meals/initial?username=${encodeURIComponent(username)}`,
      { method: 'POST', body: JSON.stringify({ Username: username }) }
    );
  },

  feedback(username: string, mealCode: string, like: boolean, initial: boolean) {
    return http('/meals/feedback', {
      method: 'POST',
      body: JSON.stringify({
        Username: username,
        MealCode: mealCode,
        Like: like,
        Initial: initial, // TRUE for initial page, FALSE for daily picks
      }),
    });
  },

  /** Optional batch helper (used by initial page) */
  sendInitialFeedback(username: string, items: Array<{ mealCode: string; like: boolean }>) {
    return Promise.all(
      items.map((it) =>
        api.feedback(username, it.mealCode, it.like, /* initial */ true)
      )
    );
  },

  biomarkers(username: string, b1: number, b2: number, b3: number) {
    return fetch(`${API_BASE}/biomarkers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        Username: username,
        "Mood": b1,
        "Energy": b2,
        "Fullness": b3,
      }),
    }).then(async (res) => {
      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
      return res.json();
    });
  },
  
  runSummaries(username: string, windowDays = 7) {
    return http<{ ok: true }>('/summaries/run', {
      method: 'POST',
      body: JSON.stringify({ Username: username, window_days: windowDays }),
    });
  },

  dailyMeals(username: string) {
    return http<{ breakfast: any; lunch: any; dinner: any }>(
      `/meals/daily?username=${encodeURIComponent(username)}`,
      { method: 'POST', body: JSON.stringify({ Username: username }) }
    );
  },

  chosenIngredients(username: string, mealCodes: string[]) {
    return http<Record<"breakfast"|"lunch"|"dinner", Record<string, {
      description?: string;
      ingredients: Record<string, string>;
      // steps is optional — we render it if present
      steps?: string[] | string;
    }>>>('/meals/ingredients', {
      method: 'POST',
      body: JSON.stringify({
        Username: username,
        MealCodes: mealCodes,
      }),
    });
  },
}