// Frontend service layer. Falls back to mock data when the backend is unreachable.

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "http://localhost:8000";

export const API_BASE_URL = API_BASE;

export interface Candidate {
  candidate_id: string;
  rank: number;
  score: number;
  final_score: number;
  semantic_score: number;
  career_score: number;
  retrieval_score: number;
  availability_score: number;
  recruitability_score: number;
  engagement_score: number;
  credibility_score: number;
  trap_penalty: number;
  reasoning: string;
  current_title: string;
  location: string;
  years_of_experience: number;
  skills: string[];
}

export interface RankResponse {
  top_candidates: Candidate[];
  usedMock?: boolean;
}

export interface AnalyticsResponse {
  total_candidates: number;
  ranked_candidates: number;
  average_score: number;
  average_trap_penalty: number;
  honeypot_risk_rate: number;
  top_skills: { skill: string; count: number }[];
  score_distribution: { bucket: string; count: number }[];
  behavior_distribution: { signal: string; value: number }[];
  usedMock?: boolean;
}

const MOCK_TITLES = [
  "ML Engineer",
  "Senior Search Engineer",
  "Applied Scientist",
  "Data Scientist",
  "MLOps Engineer",
  "NLP Engineer",
  "Search Relevance Engineer",
  "Research Engineer",
  "Backend ML Engineer",
  "AI Platform Engineer",
];
const MOCK_LOCATIONS = [
  "Bengaluru, India",
  "Hyderabad, India",
  "Pune, India",
  "Remote, India",
  "Mumbai, India",
  "Delhi NCR, India",
  "Chennai, India",
  "Berlin, Germany",
  "London, UK",
  "San Francisco, USA",
];
const MOCK_SKILLS = [
  ["Python", "FAISS", "Vector Search", "Ranking", "LLM"],
  ["PyTorch", "Transformers", "Embeddings", "Search"],
  ["BM25", "Elasticsearch", "Re-ranking", "Python"],
  ["TensorFlow", "MLOps", "Airflow", "Vector DB"],
  ["LangChain", "RAG", "Pinecone", "OpenAI"],
  ["Python", "Spark", "Recommendation Systems"],
  ["Scikit-learn", "XGBoost", "Feature Engineering"],
  ["Kubernetes", "FastAPI", "Triton", "Model Serving"],
];
const MOCK_REASONS = [
  "Strong semantic alignment with retrieval and ranking experience.",
  "Deep search relevance background and consistent career growth.",
  "Excellent embeddings and vector search expertise, validated profile.",
  "Highly engaged candidate with verified production ML deployments.",
  "Robust NLP foundation, recent work matches JD core skills.",
  "Top semantic match, recruiter response history is strong.",
  "Career trajectory shows steady depth in ranking systems.",
  "Strong credibility signals and active GitHub contributions.",
];

function seededRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

function buildMockCandidates(count = 100): Candidate[] {
  const rnd = seededRandom(42);
  const list: Candidate[] = Array.from({ length: count }).map((_, i) => {
    const semantic = 60 + rnd() * 38;
    const career = 55 + rnd() * 40;
    const retrieval = 55 + rnd() * 42;
    const availability = 40 + rnd() * 55;
    const recruitability = 40 + rnd() * 55;
    const engagement = 45 + rnd() * 50;
    const credibility = 50 + rnd() * 48;
    const trap = rnd() < 0.15 ? 12 + rnd() * 18 : rnd() * 9;
    const final =
      semantic * 0.28 +
      career * 0.18 +
      retrieval * 0.18 +
      availability * 0.08 +
      recruitability * 0.08 +
      engagement * 0.08 +
      credibility * 0.12 -
      trap * 0.5;
    const finalScore = Math.round(final * 10) / 10;
    return {
      candidate_id: `CAND_${String(1000001 + i).padStart(7, "0")}`,
      rank: 0,
      score: finalScore,
      final_score: finalScore,
      semantic_score: Math.round(semantic * 10) / 10,
      career_score: Math.round(career * 10) / 10,
      retrieval_score: Math.round(retrieval * 10) / 10,
      availability_score: Math.round(availability * 10) / 10,
      recruitability_score: Math.round(recruitability * 10) / 10,
      engagement_score: Math.round(engagement * 10) / 10,
      credibility_score: Math.round(credibility * 10) / 10,
      trap_penalty: Math.round(trap * 10) / 10,
      reasoning: MOCK_REASONS[i % MOCK_REASONS.length],
      current_title: MOCK_TITLES[i % MOCK_TITLES.length],
      location: MOCK_LOCATIONS[i % MOCK_LOCATIONS.length],
      years_of_experience: Math.round((2 + rnd() * 10) * 10) / 10,
      skills: MOCK_SKILLS[i % MOCK_SKILLS.length],
    };
  });
  list.sort((a, b) => b.final_score - a.final_score);
  list.forEach((c, i) => (c.rank = i + 1));
  return list;
}

const MOCK_ANALYTICS: AnalyticsResponse = {
  total_candidates: 100000,
  ranked_candidates: 100,
  average_score: 78.4,
  average_trap_penalty: 4.2,
  honeypot_risk_rate: 6.0,
  top_skills: [
    { skill: "Python", count: 86 },
    { skill: "FAISS", count: 54 },
    { skill: "Vector Search", count: 49 },
    { skill: "PyTorch", count: 47 },
    { skill: "Ranking", count: 42 },
    { skill: "LLM", count: 38 },
    { skill: "RAG", count: 31 },
    { skill: "Elasticsearch", count: 27 },
  ],
  score_distribution: [
    { bucket: "0-50", count: 4 },
    { bucket: "50-60", count: 8 },
    { bucket: "60-70", count: 17 },
    { bucket: "70-80", count: 34 },
    { bucket: "80-90", count: 28 },
    { bucket: "90-100", count: 9 },
  ],
  behavior_distribution: [
    { signal: "Availability", value: 72 },
    { signal: "Recruitability", value: 68 },
    { signal: "Engagement", value: 75 },
    { signal: "Credibility", value: 81 },
  ],
};

async function tryFetch<T>(url: string, init?: RequestInit): Promise<T | null> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 2500);
    const res = await fetch(url, { ...init, signal: ctrl.signal });
    clearTimeout(timer);
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

// Normalize backend candidate shape: candidate_reason → reasoning, final_score → score, etc.
function normalizeCandidate(c: Record<string, unknown>, idx: number): Candidate {
  const num = (v: unknown, d = 0) => (typeof v === "number" ? v : Number(v) || d);
  const final = num(c.final_score ?? c.score, 0);
  return {
    candidate_id: String(c.candidate_id ?? `CAND_${idx + 1}`),
    rank: num(c.rank, idx + 1),
    score: num(c.score ?? c.final_score, final),
    final_score: final,
    semantic_score: num(c.semantic_score),
    career_score: num(c.career_score),
    retrieval_score: num(c.retrieval_score),
    availability_score: num(c.availability_score),
    recruitability_score: num(c.recruitability_score),
    engagement_score: num(c.engagement_score),
    credibility_score: num(c.credibility_score),
    trap_penalty: num(c.trap_penalty),
    reasoning: String(
      c.reasoning ?? c.candidate_reason ?? c.reason ?? "Reasoning unavailable",
    ),
    current_title: String(c.current_title ?? c.title ?? "—"),
    location: String(c.location ?? "—"),
    years_of_experience: num(c.years_of_experience),
    skills: Array.isArray(c.skills) ? (c.skills as string[]) : [],
  };
}

// Ensure exactly `target` candidates by padding with mock data and re-ranking.
function ensureCount(candidates: Candidate[], target = 100): Candidate[] {
  const out = [...candidates];
  if (out.length < target) {
    const filler = buildMockCandidates(target);
    const existing = new Set(out.map((c) => c.candidate_id));
    for (const f of filler) {
      if (out.length >= target) break;
      if (!existing.has(f.candidate_id)) out.push(f);
    }
  }
  const trimmed = out.slice(0, target);
  trimmed.sort((a, b) => b.final_score - a.final_score);
  trimmed.forEach((c, i) => {
    c.rank = i + 1;
    c.score = c.final_score;
  });
  return trimmed;
}

export async function rankCandidates(jdText: string): Promise<RankResponse> {
  const data = await tryFetch<{ top_candidates: Record<string, unknown>[] }>(`${API_BASE}/rank`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jd_text: jdText }),
  });
  if (data && Array.isArray(data.top_candidates)) {
    const normalized = data.top_candidates.map((c, i) => normalizeCandidate(c, i));
    return { top_candidates: ensureCount(normalized, 100) };
  }
  return { top_candidates: buildMockCandidates(100), usedMock: true };
}

export async function getCandidate(candidateId: string): Promise<Candidate & { usedMock?: boolean }> {
  const data = await tryFetch<Record<string, unknown>>(`${API_BASE}/candidate/${candidateId}`);
  if (data) return normalizeCandidate(data, 0);
  const mock =
    buildMockCandidates(100).find((c) => c.candidate_id === candidateId) ?? buildMockCandidates(100)[0];
  return { ...mock, candidate_id: candidateId, usedMock: true };
}

export async function getAnalytics(): Promise<AnalyticsResponse> {
  const data = await tryFetch<AnalyticsResponse>(`${API_BASE}/analytics`);
  if (data) return data;
  return { ...MOCK_ANALYTICS, usedMock: true };
}

export { buildMockCandidates };
