import { useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowUpDown, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Candidate } from "@/services/api";

export function CandidateTable({ candidates }: { candidates: Candidate[] }) {
  const [desc, setDesc] = useState(true);
  const sorted = useMemo(
    () => [...candidates].sort((a, b) => (desc ? b.final_score - a.final_score : a.final_score - b.final_score)),
    [candidates, desc],
  );

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader className="bg-slate-50">
            <TableRow>
              <TableHead className="w-14">Rank</TableHead>
              <TableHead>Candidate ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Location</TableHead>
              <TableHead className="text-right">Exp (yrs)</TableHead>
              <TableHead className="text-right">
                <button
                  className="inline-flex items-center gap-1 text-xs font-semibold text-slate-700 hover:text-slate-900"
                  onClick={() => setDesc((d) => !d)}
                >
                  Final Score <ArrowUpDown className="h-3 w-3" />
                </button>
              </TableHead>
              <TableHead className="text-right">Trap</TableHead>
              <TableHead className="min-w-[260px]">Reason</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sorted.map((c) => (
              <TableRow key={c.candidate_id} className="hover:bg-slate-50/60">
                <TableCell className="font-semibold text-slate-700">#{c.rank}</TableCell>
                <TableCell className="font-mono text-xs text-slate-600">{c.candidate_id}</TableCell>
                <TableCell className="text-slate-800">{c.current_title}</TableCell>
                <TableCell className="text-slate-600">{c.location}</TableCell>
                <TableCell className="text-right text-slate-600">{c.years_of_experience.toFixed(1)}</TableCell>
                <TableCell className="text-right">
                  <span className="inline-flex min-w-[3rem] justify-center rounded-md bg-primary/10 px-2 py-0.5 font-semibold text-primary">
                    {c.final_score.toFixed(1)}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  {c.trap_penalty >= 15 ? (
                    <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100">{c.trap_penalty.toFixed(1)}</Badge>
                  ) : (
                    <span className="text-sm text-slate-500">{c.trap_penalty.toFixed(1)}</span>
                  )}
                </TableCell>
                <TableCell className="max-w-md text-sm text-slate-600">
                  <span className="line-clamp-2">{c.reasoning}</span>
                </TableCell>
                <TableCell className="text-right">
                  <Button asChild size="sm" variant="ghost">
                    <Link to="/candidate/$candidateId" params={{ candidateId: c.candidate_id }}>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
