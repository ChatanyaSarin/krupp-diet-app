// diet-web/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8000';

async function request(path: string, init?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    cache: 'no-store',
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status} ${txt}`);
  }
  return res;
}

export const api = {
  login: (u: string, p: string) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username: u, password: p }) }).then(r => r.json()),
  register: (u: string, p: string) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ username: u, password: p }) }),
  status: (u: string) =>
    request(`/user/status?username=${encodeURIComponent(u)}`).then(r => r.json()),
  setupUser: (payload: any) =>
    request('/setup_user', { method: 'POST', body: JSON.stringify(payload) }),
  initialMeals: (u: string) =>
    request('/meals/initial', { method: 'POST', body: JSON.stringify({ Username: u }) }).then(r => r.json()),
  biomarkers: (u: string, b1: number, b2: number, b3: number) =>
    request('/biomarkers', { method: 'POST', body: JSON.stringify({ Username: u, 'BIOMARKER 1': b1, 'BIOMARKER 2': b2, 'BIOMARKER 3': b3 }) }),
  dailyMeals: (u: string) =>
    request('/meals/daily', { method: 'POST', body: JSON.stringify({ Username: u }) }).then(r => r.json()),
  feedback: (u: string, code: string, like: boolean, initial: boolean) =>
    request('/meals/feedback', { method: 'POST', body: JSON.stringify({ Username: u, MealCode: code, Like: like, Initial: initial }) }),
};
