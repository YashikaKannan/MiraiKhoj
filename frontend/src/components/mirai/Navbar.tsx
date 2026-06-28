import { Link } from "@tanstack/react-router";
// import { Sparkles } from "lucide-react";

export function Navbar() {
  const linkCls =
    "text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors data-[status=active]:text-primary data-[status=active]:font-semibold";
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          {/* <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm"> */}
          <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">

            {/* <Sparkles className="h-5 w-5" /> */}
            <img src="/favicon.png" alt="MiraiKhoj" className="h-12 w-100"/>
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-base font-bold tracking-tight text-slate-900">MiraiKhoj</span>
            <span className="text-[10px] uppercase tracking-wider text-slate-500">Finding Talent Beyond Keywords</span>
          </div>
        </Link>
        <nav className="flex items-center gap-6">
          <Link to="/" className={linkCls} activeOptions={{ exact: true }}>Dashboard</Link>
          <Link to="/rank" className={linkCls}>Rank</Link>
          <Link to="/analytics" className={linkCls}>Analytics</Link>
        </nav>
      </div>
    </header>
  );
}
