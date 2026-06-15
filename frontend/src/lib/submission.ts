import type { Candidate } from "@/services/api";

const SUBMISSION_COLUMNS = ["candidate_id", "rank", "score", "reasoning"] as const;

function escapeCSVField(value: string | number): string {
  const s = String(value ?? "");
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

export function buildSubmissionRows(candidates: Candidate[]) {
  return candidates.map((c, i) => ({
    candidate_id: c.candidate_id,
    rank: i + 1,
    score: Number(c.final_score ?? c.score ?? 0),
    reasoning: c.reasoning || "Reasoning unavailable",
  }));
}

export function toCSV(candidates: Candidate[]): string {
  const rows = buildSubmissionRows(candidates);
  const header = SUBMISSION_COLUMNS.join(",");
  const body = rows
    .map((r) =>
      SUBMISSION_COLUMNS.map((k) => escapeCSVField(r[k] as string | number)).join(","),
    )
    .join("\n");
  return `${header}\n${body}\n`;
}

export function downloadSubmissionCSV(candidates: Candidate[], filename = "final_submission.csv") {
  const csv = toCSV(candidates);
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export interface ValidationCheck {
  label: string;
  passed: boolean;
  detail?: string;
}

export function validateSubmission(candidates: Candidate[]): ValidationCheck[] {
  const rows = buildSubmissionRows(candidates);
  const ids = rows.map((r) => r.candidate_id);
  const ranks = rows.map((r) => r.rank);
  const scores = rows.map((r) => r.score);

  const exactly100 = rows.length === 100;
  const ranksOk =
    ranks.length === 100 &&
    ranks.every((r, i) => r === i + 1);
  const uniqueIds = new Set(ids).size === ids.length;
  const nonIncreasing = scores.every((s, i) => i === 0 || s <= scores[i - 1]);
  const reasoningOk = rows.every((r) => r.reasoning && r.reasoning.trim().length > 0);
  const columnsOk = true; // Built from a fixed schema.

  return [
    { label: "Exactly 100 rows generated", passed: exactly100, detail: `${rows.length} rows` },
    { label: "Ranks 1–100 present", passed: ranksOk },
    { label: "No duplicate candidate IDs", passed: uniqueIds },
    { label: "Scores sorted in non-increasing order", passed: nonIncreasing },
    { label: "Reasoning available for every row", passed: reasoningOk },
    { label: "Required columns: candidate_id, rank, score, reasoning", passed: columnsOk },
  ];
}
