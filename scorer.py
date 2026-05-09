# scorer.py
# Pure scoring functions — no side effects, easy to unit-test and extend.
#
# Dimensions: Decision-Making | Team Communication | Strategic Thinking
# Questions per dimension: 3
# Scale per question: 1–5
# Max per dimension: 15

from dataclasses import dataclass

DIMENSIONS = [
    {"id": "decision_making",     "label": "Decision-Making",     "question_ids": ["q1", "q2", "q3"]},
    {"id": "team_communication",  "label": "Team Communication",  "question_ids": ["q4", "q5", "q6"]},
    {"id": "strategic_thinking",  "label": "Strategic Thinking",  "question_ids": ["q7", "q8", "q9"]},
]

# Thresholds (out of 15 per dimension)
BAND_THRESHOLDS = [
    {"band": "High",   "min": 12, "max": 15},
    {"band": "Medium", "min": 8,  "max": 11},
    {"band": "Low",    "min": 3,  "max": 7},
]

FEEDBACK = {
    "decision_making": {
        "High":   "You demonstrate strong decisiveness and sound judgment. You gather relevant information efficiently and commit to well-considered decisions without unnecessary delay. Continue to document your decision frameworks so your team can learn from your approach.",
        "Medium": "You show solid decision-making in familiar situations. To level up, practice structured frameworks (e.g. RAPID, DACI) for higher-stakes choices and work on reducing hesitation when information is incomplete.",
        "Low":    "Decision-making is an area for meaningful growth. Focus on building confidence by starting with smaller, reversible decisions and reflecting on outcomes. Seek a mentor who can help you develop a repeatable process.",
    },
    "team_communication": {
        "High":   "Your communication is a genuine team asset. You actively listen, deliver feedback constructively, and keep everyone aligned. Keep investing in this — strong communicators often become the connective tissue that makes teams exceptional.",
        "Medium": "You communicate reliably in day-to-day situations. To improve, pay attention to how your message lands on different people and practice adapting your style. In conflict or ambiguity, lean into clarity rather than silence.",
        "Low":    "Communication is a skill, not a trait — and it's very coachable. Start by focusing on one area: active listening, written clarity, or giving feedback. Even small, consistent improvements here have a disproportionate team impact.",
    },
    "strategic_thinking": {
        "High":   "You think beyond the immediate task and consistently connect day-to-day decisions to longer-term goals. This is a rare and valuable leadership quality. Look for opportunities to share your strategic perspective with senior stakeholders.",
        "Medium": "You show good strategic awareness in your domain. To grow further, practice zooming out regularly — ask 'why does this matter in 12 months?' and engage more with cross-functional priorities beyond your immediate area.",
        "Low":    "Strategic thinking develops with deliberate practice. Start by reading your organisation's goals and asking how your work connects to them. Set aside even 30 minutes a week to think about longer horizons — it compounds quickly.",
    },
}

BAND_COLORS = {
    "High":   "#1D9E75",
    "Medium": "#BA7517",
    "Low":    "#E24B4A",
}


@dataclass
class DimensionResult:
    id: str
    label: str
    score: int
    max_score: int
    percentage: float
    band: str
    feedback: str
    color: str


def get_band(score: int) -> str:
    for threshold in BAND_THRESHOLDS:
        if threshold["min"] <= score <= threshold["max"]:
            return threshold["band"]
    return "Low"


def compute_scores(answers: dict) -> dict:
    """
    answers: { "q1": 1-5, "q2": 1-5, ... "q9": 1-5 }
    Returns a structured result dict.
    """
    dimension_results = []

    for dim in DIMENSIONS:
        score = sum(answers.get(qid, 0) for qid in dim["question_ids"])
        band = get_band(score)
        result = DimensionResult(
            id=dim["id"],
            label=dim["label"],
            score=score,
            max_score=15,
            percentage=round((score / 15) * 100),
            band=band,
            feedback=FEEDBACK[dim["id"]][band],
            color=BAND_COLORS[band],
        )
        dimension_results.append(result)

    total_score = sum(r.score for r in dimension_results)
    total_max = sum(r.max_score for r in dimension_results)
    overall_percentage = round((total_score / total_max) * 100)

    return {
        "dimensions": [vars(r) for r in dimension_results],
        "total_score": total_score,
        "total_max": total_max,
        "overall_percentage": overall_percentage,
    }