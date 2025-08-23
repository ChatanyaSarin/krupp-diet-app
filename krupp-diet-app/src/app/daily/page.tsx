// diet-web/app/daily/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { getUser } from '@/lib/session';

export default function Daily() {
  const u = getUser()!;
  const [data, setData] = useState<any>(null);
  const [picked, setPicked] = useState<Record<'breakfast'|'lunch'|'dinner', string | null>>({breakfast:null,lunch:null,dinner:null});
  useEffect(()=>{ api.dailyMeals(u).then(setData); },[u]);
  if (!data) return <div className="p-6">Loading…</div>;
  const ready = picked.breakfast && picked.lunch && picked.dinner;
  async function save(){
    await api.feedback(u, picked.breakfast!, true, false);
    await api.feedback(u, picked.lunch!, true, false);
    await api.feedback(u, picked.dinner!, true, false);
    alert('Saved for today!');
  }
  const Section = ({type}:{type:'breakfast'|'lunch'|'dinner'}) => {
    const meals = data[type]; const slugs = Object.keys(meals);
    return (<div><h2 className="font-semibold capitalize mb-2">{type}</h2>
      <div className="grid md:grid-cols-2 gap-3">
        {slugs.map(slug=>{
          const sel = picked[type]===slug;
          return <button key={slug} onClick={()=>setPicked({...picked,[type]:slug})}
            className={`text-left border rounded p-3 ${sel?'border-emerald-600 ring-1 ring-emerald-600':''}`}>
            {meals[slug].long_name}
          </button>;
        })}
      </div></div>);
  };
  return (<div className="max-w-5xl mx-auto p-6 space-y-6">
    <Section type="breakfast" />
    <Section type="lunch" />
    <Section type="dinner" />
    <button disabled={!ready} onClick={save} className="bg-emerald-600 text-white rounded px-4 py-2 disabled:opacity-50">
      Save today’s picks
    </button>
  </div>);
}
