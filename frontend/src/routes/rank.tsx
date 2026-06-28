import { useEffect, useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { CheckCircle2, Download, Info, Loader2, ServerCog, Sparkles, XCircle } from "lucide-react";
import { Navbar } from "@/components/mirai/Navbar";
import { CandidateTable } from "@/components/mirai/CandidateTable";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { rankCandidates, type Candidate, API_BASE_URL } from "@/services/api";
import {
  buildSubmissionRows,
  downloadSubmissionCSV,
  validateSubmission,
} from "@/lib/submission";

export const Route = createFileRoute("/rank")({
  head: () => ({
    meta: [
      { title: "Rank Candidates — MiraiKhoj" },
      { name: "description", content: "Paste a job description and rank the Top 100 candidates with explainable AI." },
    ],
  }),
  component: RankPage,
});

const EXAMPLE_JD = `Senior ML Engineer — Search & Ranking

We are hiring an ML engineer to build and improve our semantic search and ranking systems.

Responsibilities:
- Design retrieval and re-ranking pipelines using vector search (FAISS / pgvector).
- Train and fine-tune embedding models for domain-specific retrieval.
- Build evaluation harnesses for relevance and ranking quality.
- Productionize models with low-latency serving.

Required:
- 4+ years of ML / NLP experience.
- Strong Python, PyTorch / TensorFlow.
- Experience with FAISS, Elasticsearch, BM25, learning-to-rank.
- Hands-on with LLMs, embeddings, RAG.`;

function RankPage() {
  const [jd, setJd] = useState(EXAMPLE_JD);
  const [loading, setLoading] = useState(false);
  const [candidates, setCandidates] = useState<Candidate[] | null>(null);
  const [usedMock, setUsedMock] = useState(false);

  useEffect(() => {
  const saved = sessionStorage.getItem("rank_results");

  if (saved) {
    const parsed = JSON.parse(saved);

    setCandidates(parsed.candidates);
    setUsedMock(parsed.usedMock);
  }
}, []);

  async function handleRank() {
    setLoading(true);
    const res = await rankCandidates(jd);
    setCandidates(res.top_candidates);
    setUsedMock(Boolean(res.usedMock));
    sessionStorage.setItem(
      "rank_results",
      JSON.stringify({
        candidates: res.top_candidates,
        usedMock: Boolean(res.usedMock),
      })
    );
    setLoading(false);
  }

  const avg =
    candidates && candidates.length > 0
      ? candidates.reduce((s, c) => s + c.final_score, 0) / candidates.length
      : 0;
  const flagged = candidates?.filter((c) => c.trap_penalty >= 15).length ?? 0;

  const previewRows = useMemo(
    () => (candidates ? buildSubmissionRows(candidates).slice(0, 10) : []),
    [candidates],
  );
  const checks = useMemo(
    () => (candidates ? validateSubmission(candidates) : []),
    [candidates],
  );
  const allValid = checks.length > 0 && checks.every((c) => c.passed);

  return (
    <div className="min-h-screen bg-slate-50/40">
      <Navbar />
      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Rank Top 100 Candidates</h1>
            <p className="mt-1 text-sm text-slate-600">
              Paste a job description. MiraiKhoj runs semantic retrieval, career intelligence,
              behavioral signals and trap detection to return an explained Top 100 shortlist.
            </p>
          </div>
          <ModeBadge usedMock={candidates ? usedMock : null} />
        </div>

        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Job Description</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste your JD here…"
              className="min-h-[240px] resize-y border-slate-200 bg-white font-mono text-sm"
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">{jd.length.toLocaleString()} characters</span>
              <Button onClick={handleRank} disabled={loading || jd.trim().length < 20} size="lg">
                {loading ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Ranking Top 100 candidates…</>
                ) : (
                  <><Sparkles className="mr-2 h-4 w-4" />Rank Candidates</>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {candidates && (
          <section className="mt-8 space-y-6">
            {usedMock && (
              <Alert className="border-sky-200 bg-sky-50 text-sky-900">
                <Info className="h-4 w-4 text-sky-600" />
                <AlertTitle>Demo / sandbox mode</AlertTitle>
                <AlertDescription>
                  Backend not reachable at <code className="font-mono">{API_BASE_URL}</code> — showing
                  100 deterministic mock candidates so you can explore the full submission flow.
                </AlertDescription>
              </Alert>
            )}

            <Card className="border-slate-200 shadow-sm">
              <CardContent className="grid gap-4 p-6 sm:grid-cols-3">
                <Stat label="Candidates ranked" value={String(candidates.length)} />
                <Stat label="Average final score" value={avg.toFixed(1)} />
                <Stat
                  label="Trap-flagged"
                  value={String(flagged)}
                  accent={flagged > 0 ? "text-amber-600" : undefined}
                />
              </CardContent>
            </Card>

            <div>
              <h2 className="mb-3 text-lg font-semibold text-slate-900">Top 100 Ranked Candidates</h2>
              <CandidateTable candidates={candidates} />
            </div>

            <div className="grid gap-6 lg:grid-cols-5">
              {/* Submission preview */}
              <Card className="border-slate-200 shadow-sm lg:col-span-3">
                <CardHeader className="flex flex-row items-center justify-between gap-3">
                  <div>
                    <CardTitle className="text-base">Submission Preview</CardTitle>
                    <p className="mt-1 text-xs text-slate-500">
                      Exact CSV structure for Redrob: <code className="font-mono">candidate_id,rank,score,reasoning</code>.
                      Showing first 10 of 100 rows — download for the full file.
                    </p>
                  </div>
                  <Button onClick={() => downloadSubmissionCSV(candidates)} disabled={!allValid}>
                    <Download className="mr-2 h-4 w-4" /> Download final_submission.csv
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto rounded-lg border border-slate-200">
                    <table className="w-full text-xs">
                      <thead className="bg-slate-50 text-left text-slate-600">
                        <tr>
                          <th className="px-3 py-2 font-mono font-semibold">candidate_id</th>
                          <th className="px-3 py-2 font-mono font-semibold">rank</th>
                          <th className="px-3 py-2 font-mono font-semibold">score</th>
                          <th className="px-3 py-2 font-mono font-semibold">reasoning</th>
                        </tr>
                      </thead>
                      <tbody>
                        {previewRows.map((r) => (
                          <tr key={r.candidate_id} className="border-t border-slate-100">
                            <td className="px-3 py-2 font-mono text-slate-700">{r.candidate_id}</td>
                            <td className="px-3 py-2 font-mono text-slate-700">{r.rank}</td>
                            <td className="px-3 py-2 font-mono text-slate-700">{r.score.toFixed(1)}</td>
                            <td className="px-3 py-2 text-slate-600">
                              <span className="line-clamp-1">{r.reasoning}</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="mt-3 text-xs text-slate-500">
                    Full file contains all 100 rows. Header row included; commas, quotes and newlines escaped per RFC 4180.
                  </p>
                </CardContent>
              </Card>

              {/* Validation */}
              <Card className="border-slate-200 shadow-sm lg:col-span-2">
                <CardHeader>
                  <CardTitle className="text-base">Validation Status</CardTitle>
                  <p className="mt-1 text-xs text-slate-500">
                    Submission must pass every check before download.
                  </p>
                </CardHeader>
                <CardContent className="space-y-2">
                  {checks.map((c) => (
                    <div
                      key={c.label}
                      className={`flex items-start gap-2 rounded-lg border px-3 py-2 ${
                        c.passed
                          ? "border-emerald-200 bg-emerald-50"
                          : "border-red-200 bg-red-50"
                      }`}
                    >
                      {c.passed ? (
                        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                      ) : (
                        <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" />
                      )}
                      <div className="flex-1">
                        <div
                          className={`text-sm font-medium ${
                            c.passed ? "text-emerald-900" : "text-red-900"
                          }`}
                        >
                          {c.label}
                        </div>
                        {c.detail && (
                          <div className="text-xs text-slate-600">{c.detail}</div>
                        )}
                      </div>
                    </div>
                  ))}
                  {!allValid && (
                    <Alert className="border-red-200 bg-red-50 text-red-900">
                      <XCircle className="h-4 w-4 text-red-600" />
                      <AlertTitle>Submission not ready</AlertTitle>
                      <AlertDescription>
                        Fix the failing checks above before downloading <code>final_submission.csv</code>.
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function ModeBadge({ usedMock }: { usedMock: boolean | null }) {
  if (usedMock === null) {
    return (
      <Badge variant="outline" className="gap-1.5 border-slate-200 bg-white text-slate-600">
        <ServerCog className="h-3 w-3" /> Backend: {API_BASE_URL}
      </Badge>
    );
  }
  if (usedMock) {
    return (
      <Badge className="gap-1.5 bg-amber-100 text-amber-800 hover:bg-amber-100">
        <ServerCog className="h-3 w-3" /> Demo Mode · backend unavailable, using mock candidates
      </Badge>
    );
  }
  return (
    <Badge className="gap-1.5 bg-emerald-100 text-emerald-800 hover:bg-emerald-100">
      <ServerCog className="h-3 w-3" /> Backend Mode · connected to {API_BASE_URL}
    </Badge>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-1 text-2xl font-bold text-slate-900 ${accent ?? ""}`}>{value}</div>
    </div>
  );
}
