import { AlertTriangle } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import type { Candidate } from "@/services/api";

const ROWS: { key: keyof Candidate; label: string; desc: string }[] = [
  { key: "semantic_score", label: "Semantic Score", desc: "JD meaning alignment" },
  { key: "career_score", label: "Career Score", desc: "Relevant work history" },
  { key: "retrieval_score", label: "Retrieval Score", desc: "Search & ranking system expertise" },
  { key: "availability_score", label: "Availability Score", desc: "Activity and readiness" },
  { key: "recruitability_score", label: "Recruitability Score", desc: "Response and interview behavior" },
  { key: "engagement_score", label: "Engagement Score", desc: "Recruiter interest signals" },
  { key: "credibility_score", label: "Credibility Score", desc: "Verified and complete profile" },
];

export function ScoreBreakdown({ candidate }: { candidate: Candidate }) {
  return (
    <div className="space-y-5">
      {ROWS.map((r) => {
        const value = candidate[r.key] as number;
        return (
          <div key={r.key}>
            <div className="flex items-baseline justify-between">
              <div>
                <div className="text-sm font-medium text-slate-800">{r.label}</div>
                <div className="text-xs text-slate-500">{r.desc}</div>
              </div>
              <div className="text-sm font-semibold text-slate-700">{value.toFixed(1)}</div>
            </div>
            <Progress value={value} className="mt-2 h-2" />
          </div>
        );
      })}

      <div
        className={`rounded-lg border p-4 ${
          candidate.trap_penalty >= 15
            ? "border-red-200 bg-red-50"
            : candidate.trap_penalty >= 10
              ? "border-amber-200 bg-amber-50"
              : "border-emerald-200 bg-emerald-50"
        }`}
      >
        <div className="flex items-start gap-3">
          <AlertTriangle
            className={`mt-0.5 h-5 w-5 ${
              candidate.trap_penalty >= 15
                ? "text-red-600"
                : candidate.trap_penalty >= 10
                  ? "text-amber-600"
                  : "text-emerald-600"
            }`}
          />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-slate-800">Trap Penalty</div>
              <div className="text-sm font-bold text-slate-800">{candidate.trap_penalty.toFixed(1)}</div>
            </div>
            <p className="mt-1 text-xs text-slate-600">
              Honeypot &amp; keyword-stuffing detector. Higher penalty means more suspicious profile signals.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
