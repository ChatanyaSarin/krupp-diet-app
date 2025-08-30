// app/gate/page.tsx
'use client';

import { useEffect, useState, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';

function getUserLS(): string | null {
  try { return window.localStorage.getItem('username'); } catch { return null; }
}
function saveUserLS(u: string) {
  try { window.localStorage.setItem('username', u); } catch {}
}

export default function Gate() {
  const r = useRouter();
  const qs = useSearchParams();
  const [err, setErr] = useState<string | null>(null);

  const qsUsername = useMemo(() => qs.get('username') ?? '', [qs]);

  useEffect(() => {
    const u = qsUsername || getUserLS();
    if (!u) { r.replace('/login'); return; }
    if (qsUsername) saveUserLS(qsUsername); // persist if it came from URL

    (async () => {
      try {
        const s = await api.status(u);
        if (!s.has_profile)       r.replace(`/setup?username=${encodeURIComponent(u)}`);
        else if (!s.has_initial_feedback) r.replace(`/initial?username=${encodeURIComponent(u)}`);
        else                       r.replace(`/biomarkers?username=${encodeURIComponent(u)}`);
      } catch (e: any) {
        setErr(e.message ?? String(e));
      }
    })();
  }, [r, qsUsername]);

  return (
    <div className="min-h-screen grid place-items-center p-10">
      {!err ? <p>Checking your status…</p> : <p className="text-red-600">{err}</p>}
    </div>
  );
}
