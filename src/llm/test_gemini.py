
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))
from llm.gemini_reasoner import GeminiReasoner

g = GeminiReasoner()

result = g.evaluate(
    jd="Need an AI Engineer with retrieval and FAISS experience.",
    candidate="""
AI Engineer
6 years experience
Built recommendation systems
Worked on FAISS
Production NLP
""",
    current_score=0.82,
)

print(result)