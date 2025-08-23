// diet-web/app/initial/page.tsx
'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { getUser } from '@/lib/session';
import { useRouter } from 'next/navigation';

export default function Initial() {
  const r = useRouter(); const u = getUser()!;
  const [meals, setMeals] = useState<any>({});
  const [choice, setChoice] = useState<Record<string, boolean | null>>({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.initialMeals(u).then(m => {
      setMeals(m);
      const init: Record<string, boolean|null> = {};
      Object.keys(m).forEach(k => init[k] = null);
      setChoice(init);
    });
  }, [u]);

  const slugs = Object.keys(meals);
  const likesCount = Object.values(choice).filter(v => v === true).length;

  async function submit() {
    setBusy(true);
    for (const slug of slugs) {
      const like = choice[slug] === true;
      await api.feedback(u, slug, like, true);
    }
    r.push('/biomarkers');
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-xl font-semibold mb-3">Pick the meals you like (at least one)</h1>
      <div className="grid md:grid-cols-2 gap-4">
        {slugs.map(slug => {
          const liked = choice[slug];
          return (
            <div key={slug} className="border rounded-lg p-4 space-y-2">
              <div className="font-medium">{meals[slug].long_name}</div>
              <div className="text-sm text-gray-600">… ingredients & steps preview …</div>
              <div className="flex gap-2">
                <button className={`flex-1 border rounded px-3 py-2 ${liked===true?'bg-green-600 text-white':''}`} onClick={()=>setChoice({...choice, [slug]: true})}>Like</button>
                <button className={`flex-1 border rounded px-3 py-2 ${liked===false?'bg-red-600 text-white':''}`} onClick={()=>setChoice({...choice, [slug]: false})}>Dislike</button>
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4">
        <button disabled={likesCount===0 || busy} onClick={submit}
          className="bg-emerald-600 text-white rounded px-4 py-2 disabled:opacity-50">
          {busy ? 'Saving…' : `Submit (${likesCount} liked)`}
        </button>
      </div>
    </div>
  );
}
