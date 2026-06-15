import { Link } from "@tanstack/react-router";
import { ArrowRight, MapPin, ShieldAlert, ShieldCheck, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { Candidate } from "@/services/api";

export function CandidateCard({ candidate }: { candidate: Candidate }) {
  const strong = candidate.final_score >= 80;
  const credible = candidate.credibility_score >= 75;
  const risky = candidate.trap_penalty >= 15;

  return (
    <Card className="border-slate-200 shadow-sm transition-shadow hover:shadow-md">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-xs font-medium text-slate-500">#{candidate.rank} · {candidate.candidate_id}</div>
            <h3 className="mt-1 text-base font-semibold text-slate-900">{candidate.current_title}</h3>
            <div className="mt-1 flex items-center gap-1 text-sm text-slate-500">
              <MapPin className="h-3.5 w-3.5" />
              {candidate.location}
            </div>
          </div>
          <div className="rounded-xl bg-primary/10 px-3 py-1.5 text-right">
            <div className="text-[10px] font-medium uppercase tracking-wide text-primary/80">Final</div>
            <div className="text-lg font-bold text-primary">{candidate.final_score.toFixed(1)}</div>
          </div>
        </div>

        <p className="mt-3 line-clamp-2 text-sm text-slate-600">{candidate.reasoning}</p>

        <div className="mt-3 flex flex-wrap gap-1.5">
          {strong && (
            <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-100"><Star className="mr-1 h-3 w-3" />Strong Match</Badge>
          )}
          {credible && (
            <Badge className="bg-sky-100 text-sky-700 hover:bg-sky-100"><ShieldCheck className="mr-1 h-3 w-3" />High Credibility</Badge>
          )}
          {risky && (
            <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100"><ShieldAlert className="mr-1 h-3 w-3" />Trap Risk</Badge>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="flex flex-wrap gap-1">
            {candidate.skills.slice(0, 3).map((s) => (
              <span key={s} className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{s}</span>
            ))}
          </div>
          <Button asChild variant="ghost" size="sm" className="text-primary hover:text-primary">
            <Link to="/candidate/$candidateId" params={{ candidateId: candidate.candidate_id }}>
              View <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
