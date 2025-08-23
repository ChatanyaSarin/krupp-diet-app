// diet-web/app/gate/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { getUser } from '@/lib/session';
import { useRouter } from 'next/navigation';

export default function Gate() {
  const r = useRouter();
  const [msg, setMsg] = useState('Checking status...');
  useEffect(() => {
    const u = getUser();
    if (!u) { r.replace('/login'); return; }
    api.status(u).then(s => {
      if (!s.has_profile) r.replace('/setup');
      else if (!s.has_initial_feedback) r.replace('/initial');
      else r.replace('/biomarkers');
    }).catch(e => setMsg(String(e)));
  }, [r]);
  return <div className="min-h-screen grid place-items-center">{msg}</div>;
}
