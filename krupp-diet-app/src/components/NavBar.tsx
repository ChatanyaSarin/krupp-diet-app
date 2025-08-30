"use client";

export function NavBar() {
  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#0f1d36]/70 backdrop-blur-md">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-uc-gold" />
          <span className="text-xl font-semibold tracking-tight text-white">
            Krupp<span className="text-uc-gold"> Diet</span>
          </span>
        </div>
        <nav className="hidden sm:flex items-center gap-6">
          <a className="text-slate-200 hover:text-white" href="/initial">Initial</a>
          <a className="text-slate-200 hover:text-white" href="/biomarkers">Biomarkers</a>
          <a className="text-slate-200 hover:text-white" href="/daily">Daily</a>
        </nav>
        <a href="/login" className="btn btn-outline">Sign in</a>
      </div>
      <div className="h-1 w-full bg-gradient-to-r from-uc-gold/0 via-uc-gold to-uc-gold/0" />
    </header>
  );
}
