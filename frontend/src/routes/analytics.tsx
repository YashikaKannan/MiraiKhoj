import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Navbar } from "@/components/mirai/Navbar";
import { AnalyticsChart } from "@/components/mirai/AnalyticsChart";
import { Card, CardContent } from "@/components/ui/card";
import { getAnalytics } from "@/services/api";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Analytics — MiraiKhoj" },
      { name: "description", content: "Average score, honeypot risk, top skills, and score distribution." },
    ],
  }),
  component: AnalyticsPage,
});

function AnalyticsPage() {
  const { data } = useQuery({ queryKey: ["analytics"], queryFn: getAnalytics });
  if (!data)
    return (
      <div className="min-h-screen bg-slate-50/40">
        <Navbar />
        <main className="mx-auto max-w-7xl px-6 py-10 text-sm text-slate-500">Loading analytics…</main>
      </div>
    );

  return (
    <div className="min-h-screen bg-slate-50/40">
      <Navbar />
      <main className="mx-auto max-w-7xl px-6 py-10">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Analytics</h1>
        <p className="mt-1 text-sm text-slate-600">
          Quick view of the ranked pool. Submission-critical work happens on the Rank page.
        </p>

        <section className="mt-6 grid gap-4 sm:grid-cols-2">
          <KPI label="Average Final Score" value={data.average_score.toFixed(1)} />
          <KPI
            label="Honeypot Risk Rate"
            value={`${data.honeypot_risk_rate.toFixed(1)}%`}
            accent="text-amber-600"
          />
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <AnalyticsChart
            title="Score Distribution"
            data={data.score_distribution}
            xKey="bucket"
            yKey="count"
          />
          <AnalyticsChart
            title="Top Skills"
            data={data.top_skills}
            xKey="skill"
            yKey="count"
            color="#0ea5e9"
          />
        </section>

        <Card className="mt-6 border-slate-200 shadow-sm">
          <CardContent className="p-6">
            <h3 className="text-base font-semibold text-slate-900">How MiraiKhoj ranks</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">
              MiraiKhoj protects against keyword stuffing by combining semantic fit with career
              consistency, behavioral signals, credibility, and trap penalties — producing an
              explainable, recruiter-ready Top 100 shortlist.
            </p>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

function KPI({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <Card className="border-slate-200 shadow-sm">
      <CardContent className="p-5">
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
        <div className={`mt-1 text-2xl font-bold text-slate-900 ${accent ?? ""}`}>{value}</div>
      </CardContent>
    </Card>
  );
}
