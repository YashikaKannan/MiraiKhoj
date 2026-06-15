import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Briefcase, MapPin, ShieldAlert, ShieldCheck } from "lucide-react";
import { Navbar } from "@/components/mirai/Navbar";
import { ScoreBreakdown } from "@/components/mirai/ScoreBreakdown";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getCandidate } from "@/services/api";

export const Route = createFileRoute("/candidate/$candidateId")({
  head: ({ params }) => ({
    meta: [
      { title: `Candidate ${params.candidateId} — MiraiKhoj` },
      { name: "description", content: "Explainable candidate score breakdown and behavioral intelligence." },
    ],
  }),
  component: CandidateDetails,
});

function CandidateDetails() {
  const { candidateId } = Route.useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["candidate", candidateId],
    queryFn: () => getCandidate(candidateId),
  });

  return (
    <div className="min-h-screen bg-slate-50/40">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Button asChild variant="ghost" size="sm" className="mb-4 -ml-2 text-slate-600">
          <Link to="/rank"><ArrowLeft className="mr-1 h-4 w-4" /> Back to results</Link>
        </Button>

        {isLoading || !data ? (
          <div className="text-sm text-slate-500">Loading candidate…</div>
        ) : (
          <>
            <Card className="border-slate-200 shadow-sm">
              <CardContent className="p-7">
                <div className="flex flex-wrap items-start justify-between gap-6">
                  <div>
                    <div className="text-xs font-mono uppercase tracking-wider text-slate-500">
                      {data.candidate_id} · Rank #{data.rank || "—"}
                    </div>
                    <h1 className="mt-2 text-2xl font-bold text-slate-900">{data.current_title}</h1>
                    <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-600">
                      <span className="inline-flex items-center gap-1.5"><MapPin className="h-4 w-4" />{data.location}</span>
                      <span className="inline-flex items-center gap-1.5"><Briefcase className="h-4 w-4" />{data.years_of_experience.toFixed(1)} yrs experience</span>
                    </div>
                  </div>
                  <div className="rounded-2xl bg-primary/10 px-5 py-3 text-center">
                    <div className="text-[10px] font-medium uppercase tracking-wide text-primary/80">Final Score</div>
                    <div className="text-3xl font-bold text-primary">{data.final_score.toFixed(1)}</div>
                  </div>
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                  {data.trap_penalty >= 15 ? (
                    <Badge className="bg-red-100 text-red-700 hover:bg-red-100"><ShieldAlert className="mr-1 h-3 w-3" />Trap risk detected</Badge>
                  ) : data.trap_penalty < 10 ? (
                    <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100"><ShieldCheck className="mr-1 h-3 w-3" />Safe profile</Badge>
                  ) : (
                    <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100">Moderate trap signals</Badge>
                  )}
                </div>

                <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Why this candidate</div>
                  <p className="mt-1 text-sm leading-relaxed text-slate-700">{data.reasoning}</p>
                </div>

                <div className="mt-5">
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Skills</div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {data.skills.map((s) => (
                      <Badge key={s} variant="secondary" className="bg-slate-100 text-slate-700 hover:bg-slate-100">{s}</Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="mt-6 grid gap-6 lg:grid-cols-3">
              <Card className="border-slate-200 shadow-sm lg:col-span-2">
                <CardHeader><CardTitle className="text-base">Explainable Score Breakdown</CardTitle></CardHeader>
                <CardContent><ScoreBreakdown candidate={data} /></CardContent>
              </Card>

              <Card className="border-slate-200 shadow-sm">
                <CardHeader><CardTitle className="text-base">Behavioral Intelligence</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { label: "Availability", v: data.availability_score },
                    { label: "Recruitability", v: data.recruitability_score },
                    { label: "Engagement", v: data.engagement_score },
                    { label: "Credibility", v: data.credibility_score },
                  ].map((b) => (
                    <div key={b.label} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                      <span className="text-sm text-slate-700">{b.label}</span>
                      <span className="text-sm font-semibold text-slate-900">{b.v.toFixed(1)}</span>
                    </div>
                  ))}
                  <div className="rounded-lg border border-slate-200 p-3 text-xs text-slate-600">
                    Behavioral signals are derived from response history, recruiter engagement,
                    profile completeness, and verification.
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
