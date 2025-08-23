// diet-web/app/login/page.tsx
'use client';
import { useState } from 'react';
import { api } from '@/lib/api';
import { setUser } from '@/lib/session';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [username, setU] = useState('');
  const [password, setP] = useState('');
  const [newPass, setNP] = useState('');
  const [needsPass, setNeedsPass] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const r = useRouter();

  async function onLogin() {
    setBusy(true); setErr(null);
    try {
      const resp = await api.login(username, password);
      if (resp?.needsPassword) setNeedsPass(true);
      else { setUser(username); r.push('/gate'); }
    } catch (e:any) { setErr(e.message); } finally { setBusy(false); }
  }

  async function onSavePass() {
    setBusy(true); setErr(null);
    try {
      await api.register(username, newPass);
      setUser(username); r.push('/gate');
    } catch (e:any) { setErr(e.message); } finally { setBusy(false); }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow p-6 space-y-4">
        <h1 className="text-xl font-semibold">Krupp Diet Study</h1>
        <input className="w-full border rounded px-3 py-2" placeholder="Username" value={username} onChange={e=>setU(e.target.value)} />
        {!needsPass ? (
          <>
            <input className="w-full border rounded px-3 py-2" placeholder="Password" type="password" value={password} onChange={e=>setP(e.target.value)} />
            <button className="w-full bg-emerald-600 text-white rounded px-3 py-2 disabled:opacity-50" disabled={busy} onClick={onLogin}>
              {busy ? '...' : 'Log in'}
            </button>
          </>
        ) : (
          <>
            <input className="w-full border rounded px-3 py-2" placeholder="Create password" type="password" value={newPass} onChange={e=>setNP(e.target.value)} />
            <button className="w-full bg-emerald-600 text-white rounded px-3 py-2 disabled:opacity-50" disabled={busy} onClick={onSavePass}>
              {busy ? '...' : 'Save & continue'}
            </button>
          </>
        )}
        {err && <p className="text-sm text-red-600">{err}</p>}
      </div>
    </div>
  );
}
