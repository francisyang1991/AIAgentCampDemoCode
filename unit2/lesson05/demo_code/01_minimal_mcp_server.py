"""
01 · Minimal FastMCP ResuMatch Server — the "BUILD your own Server" half of L5
==============================================================================
This file IS an MCP Server. Do NOT run it to "chat" with it.
Scripts 02 / 04 / 05 start it as a CHILD PROCESS over stdio, then an Agent (or
the MCP Inspector) connects and calls its tools / reads its resources.

You *can* launch it by hand to confirm it boots (it enters stdio listening
mode and waits for a client; press Ctrl+C to exit):
    python 01_minimal_mcp_server.py
    # or the official quickstart way:  uv run mcp dev 01_minimal_mcp_server.py

The three core moves (mirror the slides):
  1) mcp = FastMCP("resumatch")     create a Server (name = what Hosts show)
  2) @mcp.tool()                    decorate a function -> a callable tool
     @mcp.resource("scheme://{x}")  decorate a function -> a read-only resource
     @mcp.prompt(title="...")       decorate a function -> a reusable prompt
  3) mcp.run(transport="stdio")     start; stdout carries JSON-RPC (never print!)

@mcp.tool() is the cross-process cousin of Unit-1's @function_tool: BOTH build
the JSON Schema from the type hints + docstring. The difference is that an MCP
tool is STANDARDIZED and CROSS-PROCESS — any MCP-capable client (Claude,
Cursor, VS Code, our own Agent) can reuse it. That reusability, not "the code
isn't yours", is why parse_jd / score_resume become a Server here.

ResuMatch theme (flagship, whole course): this Server exposes the two proprietary
job-hunt tools —
  · parse_jd(jd_text)                    -> {required_skills, min_years_experience, word_count}
  · score_resume(resume_text, skills)    -> {match_score, matched, missing}
plus the read-only scoring rubric as a resource:
  · rubric://{role}                      -> the scoring breakdown for any role
and a bonus reusable prompt improve_resume. The scores are computed IN CODE
(deterministic, reproducible), never guessed by a model — the trust foundation
of the whole project. Non-job-hunt topics: keep the shape, swap the two tools.

Design bar (麻雀虽小五脏俱全):
  · structured dict returns with fixed keys (a downstream Agent / UI can rely on them);
  · never fabricate — every number is derived from the input text, so an empty
    or skill-less input yields honest zeros / empty lists, not made-up matches;
  · a `python 01_...py --selftest` path runs the pure tool logic offline, with
    no MCP transport and no model, so you can verify correctness in one second.
"""
from __future__ import annotations

import re
import sys

from mcp.server.fastmcp import FastMCP

# The MCP Server. The name is the display name connecting clients (Inspector,
# our Agent) will show.
mcp = FastMCP("resumatch")

# A tiny, readable skill lexicon. A real project would load a larger / configurable
# one (or hit a jobs API); this is enough to demo deterministic extraction and to
# keep the demo fully offline. Lowercase — matching is case-insensitive.
_SKILL_BANK = [
    "python", "sql", "react", "typescript", "java", "go",
    "aws", "gcp", "docker", "kubernetes", "pytorch", "tensorflow",
    "llm", "rag", "agent", "fastapi", "pandas", "spark", "mlops", "nlp",
]


# ---------------------------------------------------------------------------
# Tool 1 — parse_jd: turn a raw JD into structured fields.
# ---------------------------------------------------------------------------
@mcp.tool()
def parse_jd(jd_text: str) -> dict:
    """Parse a job description into structured fields.

    The required_skills list is meant to be fed straight into score_resume.
    Everything is derived from the text itself — nothing is invented.

    Args:
        jd_text: Raw job-description text pasted by the user.
    """
    text = (jd_text or "").lower()
    # Deterministic keyword hit against the lexicon (a naive substring match;
    # improving it — word boundaries, negation handling — is an Extra Challenge).
    required_skills = [s for s in _SKILL_BANK if s in text]
    # Minimum years of experience, if the JD states one (e.g. "5+ years" / "5 年").
    years = re.search(r"(\d+)\s*\+?\s*(?:年|years?)", text)
    min_years_experience = int(years.group(1)) if years else 0
    return {
        "required_skills": required_skills,
        "min_years_experience": min_years_experience,
        "word_count": len((jd_text or "").split()),
    }


# ---------------------------------------------------------------------------
# Tool 2 — score_resume: score a resume against a required-skills list.
# ---------------------------------------------------------------------------
@mcp.tool()
def score_resume(resume_text: str, required_skills: list[str]) -> dict:
    """Score how well a resume matches the required skills (0-100).

    The list[str] type hint becomes an array-typed JSON Schema automatically —
    no schema written by hand. match_score is computed in code (matched / total),
    so it is reproducible and cannot be inflated by a model guess.

    Args:
        resume_text: Plain-text resume content.
        required_skills: Skills to check for (typically parse_jd's required_skills).
    """
    text = (resume_text or "").lower()
    matched = [s for s in required_skills if s.lower() in text]
    missing = [s for s in required_skills if s.lower() not in text]
    match_score = round(100 * len(matched) / len(required_skills)) if required_skills else 0
    return {"match_score": match_score, "matched": matched, "missing": missing}


# ---------------------------------------------------------------------------
# Resource — rubric://{role}: the read-only scoring rubric, one per role.
# ---------------------------------------------------------------------------
# The {role} segment in the URI template becomes the function argument. Any
# client can read the SAME standard, which is the point of a Resource:
# read-only data (like HTTP GET), no side effects.
@mcp.resource("rubric://{role}")
def get_rubric(role: str) -> str:
    """Return the scoring rubric for a given role."""
    return (
        f"Rubric for {role}: hard skills 60%, "
        "years of experience 30%, measurable impact 10%."
    )


# ---------------------------------------------------------------------------
# Prompt — improve_resume: a reusable prompt template the Host can offer.
# ---------------------------------------------------------------------------
@mcp.prompt(title="Improve Resume")
def improve_resume(resume_text: str, missing_skills: str) -> str:
    """A reusable prompt: rewrite a resume to surface the missing skills."""
    return (
        f"Rewrite this resume to truthfully surface these skills where the "
        f"candidate genuinely has them: {missing_skills}. Never invent "
        f"experience the candidate does not have.\n\nResume:\n{resume_text}"
    )


def _selftest() -> None:
    """Offline smoke test of the pure tool logic — no MCP transport, no model.

    Runs with:  python 01_minimal_mcp_server.py --selftest
    Proves the two tools are deterministic and grounded in the input.
    """
    jd = "Senior ML Engineer. 5+ years, strong Python, PyTorch, RAG and Docker; AWS a plus."
    resume = "3 years Python backend with FastAPI; trained models in PyTorch; ships via Docker."
    parsed = parse_jd(jd)
    report = score_resume(resume, parsed["required_skills"])
    print("[自检] parse_jd     ->", parsed)
    print("[自检] score_resume ->", report)
    print("[自检] rubric       ->", get_rubric("senior-ml-engineer"))
    # A tiny invariant: matched + missing must cover exactly the required skills,
    # and the score must be the honest coverage ratio.
    assert set(report["matched"]) | set(report["missing"]) == set(parsed["required_skills"])
    expected = round(100 * len(report["matched"]) / len(parsed["required_skills"]))
    assert report["match_score"] == expected
    print("[自检] 通过：命中+缺失 = JD 全部硬技能，分数=程序算出的覆盖率（不靠模型）。")


if __name__ == "__main__":
    # --selftest: verify the tools offline. Otherwise: run as a real MCP Server.
    if "--selftest" in sys.argv:
        _selftest()
    else:
        # stdout carries JSON-RPC — NEVER print() to it. Status goes to stderr.
        print("resumatch server on stdio (waiting for a client)…", file=sys.stderr)
        mcp.run(transport="stdio")
