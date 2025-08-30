// diet-web/app/biomarkers/page.tsx
'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { getUser } from '@/lib/session';
import { useRouter } from 'next/navigation';

export default function Biomarkers() {
  const r = useRouter(); const u = getUser()!;
  const [b1,setB1]=useState('5'),[b2,setB2]=useState('5'),[b3,setB3]=useState('5');
  const [busy,setBusy]=useState(false);
  async function submit(){
    setBusy(true);
    await api.biomarkers(u, +b1, +b2, +b3);
    r.push('/daily');
  }
  return (<div className="max-w-md mx-auto p-6 space-y-3">
    <h1 className="text-xl font-semibold">How are you today?</h1>
    {[['Biomarker 1',b1,setB1],['Biomarker 2',b2,setB2],['Biomarker 3',b3,setB3]].map(([label,val,setter]:any)=>(
      <input key={label} className="w-full border rounded text-black px-3 py-2" placeholder={`${label} (0–10)`}
        value={val} onChange={(e)=>setter(e.target.value)} />
    ))}
    <button disabled={busy} onClick={submit} className="bg-emerald-600 text-white rounded px-3 py-2">Continue</button>
  </div>);
}
