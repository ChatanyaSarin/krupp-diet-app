// diet-web/app/setup/page.tsx
'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { getUser } from '@/lib/session';
import { useRouter } from 'next/navigation';

export default function Setup() {
  const r = useRouter();
  const u = getUser()!;
  const [ft, setFt] = useState('5');
  const [inch, setInch] = useState('10');
  const [wt, setWt] = useState('160');
  const [goals, setGoals] = useState('bulk, energy');
  const [restr, setRestr] = useState('vegetarian');
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    const height = parseInt(ft) * 12 + parseInt(inch);
    await api.setupUser({ Username: u, Height: height, Weight: parseInt(wt), Goals: goals, DietaryRestrictions: restr });
    r.push('/initial');
  }

  return (
    <div className="max-w-xl mx-auto p-6 space-y-4">
      <h1 className="text-xl font-semibold">Profile</h1>
      <div className="grid grid-cols-2 gap-3">
        <input className="border rounded px-3 py-2" placeholder="Feet" value={ft} onChange={e=>setFt(e.target.value)} />
        <input className="border rounded px-3 py-2" placeholder="Inches" value={inch} onChange={e=>setInch(e.target.value)} />
      </div>
      <input className="border rounded px-3 py-2 w-full" placeholder="Weight (lbs)" value={wt} onChange={e=>setWt(e.target.value)} />
      <input className="border rounded px-3 py-2 w-full" placeholder="Goals" value={goals} onChange={e=>setGoals(e.target.value)} />
      <input className="border rounded px-3 py-2 w-full" placeholder="Dietary restrictions" value={restr} onChange={e=>setRestr(e.target.value)} />
      <button className="bg-emerald-600 text-white rounded px-3 py-2 disabled:opacity-50" disabled={busy} onClick={submit}>
        {busy ? '...' : 'Save & continue'}
      </button>
    </div>
  );
}
