import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import {
  ArrowRight,
  BarChart3,
  Brain,
  ChevronRight,
  Database,
  Filter,
  ShieldAlert,
  Sparkles,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";
import { Navbar } from "@/components/mirai/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { getAnalytics } from "@/services/api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "MiraiKhoj — Finding Talent Beyond Keywords" },
      {
        name: "description",
        content:
          "Explainable AI candidate discovery using semantic search, behavioral intelligence, and honeypot detection.",
      },
      { property: "og:title", content: "MiraiKhoj — Finding Talent Beyond Keywords" },
      {
        property: "og:description",
        content: "Recruiter-ready shortlist powered by semantic retrieval and explainable score fusion.",
      },
    ],
  }),
  component: Dashboard,
});

const PIPELINE = [
  { icon: FileText, label: "Job Description" },
  { icon: Database, label: "FAISS Retrieval" },
  { icon: Brain, label: "Career Intelligence" },
  { icon: TrendingUp, label: "Behavioral Signals" },
  { icon: ShieldAlert, label: "Trap Detection" },
  { icon: Filter, label: "Score Fusion" },
  { icon: Target, label: "Final Ranking" },
];

function Dashboard() {
  const { data } = useQuery({ queryKey: ["analytics"], queryFn: getAnalytics });
  const kpis = [
    { label: "Total Candidates", value: (data?.total_candidates ?? 100000).toLocaleString(), icon: Users, accent: "bg-sky-50 text-sky-600" },
    { label: "Ranked Candidates", value: (data?.ranked_candidates ?? 100).toLocaleString(), icon: Target, accent: "bg-emerald-50 text-emerald-600" },
    { label: "Average Final Score", value: (data?.average_score ?? 78.4).toFixed(1), icon: BarChart3, accent: "bg-indigo-50 text-indigo-600" },
    { label: "Honeypot Risk Rate", value: `${(data?.honeypot_risk_rate ?? 6).toFixed(1)}%`, icon: ShieldAlert, accent: "bg-amber-50 text-amber-600" },
  ];

  return (
    <div className="min-h-screen bg-slate-50/40">
      <Navbar />

      <main className="mx-auto max-w-7xl px-6 py-12">
        {/* Hero */}
        <section className="rounded-3xl border border-slate-200 bg-gradient-to-br from-white via-sky-50/40 to-white p-10 shadow-sm">
          {/* <div className="inline-flex items-center gap-2 rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700">
            <Sparkles className="h-3.5 w-3.5" /> Redrob Data &amp; AI Challenge
          </div> */}
          <h1 className="mt-5 max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            MiraiKhoj - <span className="text-primary">Finding Talent Beyond Keywords</span>
          </h1>
          <p className="mt-4 max-w-2xl text-base text-slate-600 sm:text-lg">
            Explainable AI candidate discovery using semantic search, behavioral intelligence,
            and honeypot detection.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button asChild size="lg" className="rounded-full px-6">
              <Link to="/rank">
                Start Ranking <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="rounded-full px-6">
              <Link to="/analytics">View Analytics</Link>
            </Button>
          </div>
        </section>

        {/* KPIs */}
        <section className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {kpis.map((k) => (
            <Card key={k.label} className="border-slate-200 shadow-sm">
              <CardContent className="p-6">
                <div className={`inline-flex h-10 w-10 items-center justify-center rounded-lg ${k.accent}`}>
                  <k.icon className="h-5 w-5" />
                </div>
                <div className="mt-4 text-xs font-medium uppercase tracking-wide text-slate-500">{k.label}</div>
                <div className="mt-1 text-2xl font-bold text-slate-900">{k.value}</div>
              </CardContent>
            </Card>
          ))}
        </section>

        {/* Pipeline */}
        <section className="mt-10">
          <h2 className="text-lg font-semibold text-slate-900">Ranking Pipeline</h2>
          <p className="mt-1 text-sm text-slate-600">From job description to recruiter-ready shortlist.</p>
          <div className="mt-5 flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            {PIPELINE.map((step, i) => (
              <div key={step.label} className="flex items-center gap-2">
                <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
                  <step.icon className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium text-slate-700">{step.label}</span>
                </div>
                {i < PIPELINE.length - 1 && <ChevronRight className="h-4 w-4 text-slate-300" />}
              </div>
            ))}
          </div>
        </section>

        {/* Value prop */}
        <section className="mt-10 grid gap-6 lg:grid-cols-3">
          <Card className="border-slate-200 lg:col-span-2 shadow-sm">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-slate-900">Beyond keyword matching</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                MiraiKhoj does not only match keywords. It checks career evidence, behavioral quality,
                credibility, and suspicious profile patterns - so every shortlisted candidate has signals
                a recruiter can actually trust.
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {[
                  "Explainable score fusion",
                  "Behavioral intelligence",
                  "Honeypot-aware ranking",
                  "Recruiter-ready shortlist",
                ].map((t) => (
                  <div key={t} className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                    <span className="text-sm text-slate-700">{t}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card className="border-slate-200 shadow-sm">
            <CardContent className="p-6">
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Sparkles className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-slate-900">Ready in seconds</h3>
              <p className="mt-2 text-sm text-slate-600">
                Paste a JD and get a ranked, explained shortlist with score breakdowns and trap warnings.
              </p>
              <Button asChild className="mt-4 w-full">
                <Link to="/rank">Try it now</Link>
              </Button>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}
