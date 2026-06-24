from __future__ import annotations
from google.api_core.exceptions import ResourceExhausted

import json
import os

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class GeminiReasoner:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def evaluate_batch(self, jd: str, candidates: list[dict]) -> list[dict]:

        prompt = f"""
           You are a Principal Engineering Hiring Manager at a top technology company.

            You are selecting candidates for interview.

            Do NOT rank based on keyword matching.

            Reason like an experienced recruiter.

            Evaluate each candidate using:

            • Current role relevance
            • Production engineering experience
            • Career progression
            • Retrieval/Search systems
            • Recommendation systems
            • Large-scale backend systems
            • LLM / GenAI experience
            • System Design
            • Product company experience
            • Leadership and ownership
            • Overall interview readiness

            Prefer candidates who have actually built scalable production systems rather than simply mentioning technologies.

            For every candidate return ONLY valid JSON.

            [
            {{
            "candidate_id":"...",
            "fit_score":91,
            "interview_recommendation":"Strong Yes",
            "strengths":[
            "...",
            "..."
            ],
            "risks":[
            "..."
            ],
            "reason":"Two to three recruiter-style sentences explaining why this candidate should or should not be interviewed."
            }}
            ]
            """

        try:

            response = self.model.generate_content(prompt)

            text = response.text.strip()

            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "").strip()

            return json.loads(text)

        except ResourceExhausted:

            print("Gemini quota exceeded. Falling back to rule-based ranking.")

            return [
                {
                    "candidate_id": c["candidate_id"],
                    "fit_score": int(c["current_score"] * 100),
                }
                for c in candidates
            ]

        except Exception as e:

            print(e)

            return [
                {
                    "candidate_id": c["candidate_id"],
                    "fit_score": int(c["current_score"] * 100),
                    "reason": "LLM evaluation failed."
                }
                for c in candidates
            ]