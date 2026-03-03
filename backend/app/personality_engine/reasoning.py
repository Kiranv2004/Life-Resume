"""
Interpretable Reasoning Engine
────────────────────────────────
Explains WHY each trait score was assigned using behavioral signals.
Predicts cognitive role fit and work-style preference.
"""
from __future__ import annotations
from typing import Any, Dict, List


# ─────────────────────────────────────────────────────────────
# 1. TRAIT REASONING
# ─────────────────────────────────────────────────────────────

def _level(score: float) -> str:
    """Return a human-friendly level word matching a 0-100 score."""
    if score >= 75:
        return "strong"
    if score >= 55:
        return "moderate"
    if score >= 35:
        return "developing"
    return "low"


def compute_reasoning(traits: Dict[str, float], metrics: Dict[str, Any]) -> Dict[str, str]:
    """
    Return a human-readable explanation for each personality trait.
    Each explanation references the EXACT same factors used in scoring
    so the text always matches the displayed percentage.
    """
    r: Dict[str, str] = {}

    # ── Analytical ─────────────────────────────────────────────
    cx = metrics.get("complexity_handling", 0)
    files_per = metrics.get("avg_files_per_commit", 0)
    a_score = traits["analytical"]
    a_lev = _level(a_score)
    if a_score >= 65:
        r["analytical"] = (
            f"High-complexity contributions (avg complexity {cx:.1f}, {files_per:.1f} files/commit) — "
            "changes frequently involve multi-file refactors and algorithmic depth, "
            f"placing analytical ability in the {a_lev} range."
        )
    elif a_score >= 35:
        r["analytical"] = (
            f"Moderate complexity in commits (complexity {cx:.1f}, {files_per:.1f} files/commit) — "
            f"a mix of routine updates and deeper changes gives a {a_lev} analytical profile."
        )
    else:
        r["analytical"] = (
            f"Commits are narrowly scoped (complexity {cx:.1f}, {files_per:.1f} files/commit) — "
            f"incremental, focused changes result in a {a_lev} analytical signal."
        )

    # ── Creativity ─────────────────────────────────────────────
    exp = metrics.get("experimentation_index", 0)
    lang_div = metrics.get("language_diversity", 0)
    c_score = traits["creativity"]
    c_lev = _level(c_score)
    if c_score >= 65:
        r["creativity"] = (
            f"Experimentation rate of {exp:.0%} across {lang_div:.0f} languages drives a {c_lev} creativity score — "
            "frequent new projects and diverse tech exploration push this trait high."
        )
    elif c_score >= 35:
        r["creativity"] = (
            f"Balanced exploration ({lang_div:.0f} languages, {exp:.0%} new-repo rate) — "
            f"a mix of maintenance and experimentation produces a {c_lev} creativity signal."
        )
    else:
        r["creativity"] = (
            f"Deep-focus pattern across {lang_div:.0f} languages (experimentation {exp:.0%}) — "
            f"preference for refining existing work over exploring new domains gives a {c_lev} score."
        )

    # ── Discipline ─────────────────────────────────────────────
    consistency = metrics.get("commit_consistency", 0)
    active_days = metrics.get("active_days_ratio", 0)
    total_commits = metrics.get("total_commits", 0)
    d_score = traits["discipline"]
    d_lev = _level(d_score)
    stddev_h = consistency / 3600
    if total_commits < 5:
        r["discipline"] = (
            f"Insufficient commit history ({total_commits} commits) — not enough data to "
            f"establish a reliable discipline pattern, resulting in a {d_lev} score."
        )
    elif d_score >= 65:
        r["discipline"] = (
            f"Consistent commit rhythm — {active_days:.0%} active days, stddev {stddev_h:.0f}h, "
            f"{total_commits} total commits. Strong temporal regularity yields a {d_lev} discipline score."
        )
    elif d_score >= 35:
        r["discipline"] = (
            f"Moderate regularity — stddev {stddev_h:.0f}h between commits, {active_days:.0%} active days, "
            f"{total_commits} commits. Sprint-like cadence with gaps gives a {d_lev} discipline score."
        )
    else:
        r["discipline"] = (
            f"Irregular commit cadence — stddev {stddev_h:.0f}h, only {active_days:.0%} active days over "
            f"{total_commits} commits. Long gaps between bursts yield a {d_lev} discipline score."
        )

    # ── Collaboration ──────────────────────────────────────────
    ci = metrics.get("collaboration_index", 0)
    prs = metrics.get("pull_requests", 0)
    co_score = traits["collaboration"]
    co_lev = _level(co_score)
    if co_score >= 65:
        r["collaboration"] = (
            f"Active team contributor — {prs} PRs, collaboration index {ci:.2f}. "
            f"Code-review participation and PR activity drive a {co_lev} collaboration score."
        )
    elif co_score >= 35:
        r["collaboration"] = (
            f"Some collaborative activity — {prs} PRs, collab index {ci:.2f}. "
            f"Predominantly independent work with occasional team interaction gives a {co_lev} score."
        )
    else:
        r["collaboration"] = (
            f"Mostly solo contributions — collab index {ci:.2f}, {prs} PRs opened. "
            f"Independent repository work with minimal PR discussion results in a {co_lev} score."
        )

    # ── Adaptability ───────────────────────────────────────────
    fd = metrics.get("focus_depth", 0)
    churn = metrics.get("code_churn_ratio", 0)
    ad_score = traits["adaptability"]
    ad_lev = _level(ad_score)
    if ad_score >= 65:
        r["adaptability"] = (
            f"High scope flexibility — focus depth {fd:.0f} total changes/commit, {churn:.0%} code churn. "
            f"Frequent refactoring and large-scope changes produce a {ad_lev} adaptability score."
        )
    elif ad_score >= 35:
        r["adaptability"] = (
            f"Moderate scope comfort — focus depth {fd:.0f}, code churn {churn:.0%}. "
            f"Handles both incremental and broader changes, yielding a {ad_lev} adaptability score."
        )
    else:
        r["adaptability"] = (
            f"Narrow scope pattern — focus depth {fd:.0f}, code churn {churn:.0%}. "
            f"Prefers focused, minimal-change commits, resulting in a {ad_lev} adaptability score."
        )

    # ── Learning Velocity ──────────────────────────────────────
    repos = metrics.get("total_repos", 0)
    lv_score = traits["learning_velocity"]
    lv_lev = _level(lv_score)
    if lv_score >= 65:
        r["learning_velocity"] = (
            f"Rapid tech adoption — {exp:.0%} experimentation across {repos} repos and {lang_div:.0f} languages. "
            f"Broad, fast-paced exploration produces a {lv_lev} learning velocity."
        )
    elif lv_score >= 35:
        r["learning_velocity"] = (
            f"Steady learner — {exp:.0%} experimentation, {repos} repos, {lang_div:.0f} languages. "
            f"Gradual skill expansion gives a {lv_lev} learning velocity."
        )
    else:
        r["learning_velocity"] = (
            f"Depth-first approach — {exp:.0%} experimentation, {repos} repos, {lang_div:.0f} languages. "
            f"Focus on mastering existing stacks results in a {lv_lev} learning velocity."
        )

    # ── Risk Appetite ──────────────────────────────────────────
    bursts = metrics.get("burst_session_count", 0)
    ra_score = traits["risk_appetite"]
    ra_lev = _level(ra_score)
    if ra_score >= 65:
        r["risk_appetite"] = (
            f"High experimentation ({exp:.0%}) with {bursts} burst coding sessions — "
            f"appetite for experimental projects and intense sprints gives a {ra_lev} risk profile."
        )
    elif ra_score >= 35:
        r["risk_appetite"] = (
            f"Moderate risk-taking — {exp:.0%} experimentation, {bursts} burst sessions. "
            f"Balances proven tools with occasional experiments for a {ra_lev} risk profile."
        )
    else:
        r["risk_appetite"] = (
            f"Conservative approach — {exp:.0%} experimentation, {bursts} burst sessions. "
            f"Preference for stable, proven tools yields a {ra_lev} risk profile."
        )

    # ── Stress Stability ───────────────────────────────────────
    pi = metrics.get("persistence_index", 0)
    merge_ratio = metrics.get("pr_merge_ratio", 0)
    ss_score = traits["stress_stability"]
    ss_lev = _level(ss_score)
    if ss_score >= 65:
        r["stress_stability"] = (
            f"Clean resolution pattern — persistence index {pi:.2f}, PR merge rate {merge_ratio:.0%}. "
            f"Low fix/retry commits and reliable merges indicate {ss_lev} stress stability."
        )
    elif ss_score >= 35:
        r["stress_stability"] = (
            f"Iterative debugging style — persistence index {pi:.2f}, PR merge rate {merge_ratio:.0%}. "
            f"Some fix/bug commits with moderate revisiting gives a {ss_lev} stress stability score."
        )
    else:
        r["stress_stability"] = (
            f"Frequent revisits — persistence index {pi:.2f}, PR merge rate {merge_ratio:.0%}. "
            f"Higher fix/retry commit ratio suggests a {ss_lev} stress stability profile."
        )

    return r


# ─────────────────────────────────────────────────────────────
# 2. COGNITIVE ROLE PREDICTION
# ─────────────────────────────────────────────────────────────

_ROLES = [
    {
        "role": "Backend / Systems Engineer",
        "confidence": lambda t: (t["analytical"] * 0.4 + (100 - t["collaboration"]) * 0.3 + t["discipline"] * 0.3) / 100,
        "reason": "High complexity handling with independent work preference maps strongly to backend systems architecture and infrastructure work.",
    },
    {
        "role": "Startup Engineer",
        "confidence": lambda t: (t["creativity"] * 0.4 + t["adaptability"] * 0.35 + t["risk_appetite"] * 0.25) / 100,
        "reason": "High experimentation rate and adaptability signals match the fast-moving, context-switching demands of early-stage product development.",
    },
    {
        "role": "Team Maintainer / Tech Lead",
        "confidence": lambda t: (t["collaboration"] * 0.4 + t["discipline"] * 0.35 + t["stress_stability"] * 0.25) / 100,
        "reason": "Strong collaboration combined with disciplined commit patterns and high stress stability indicates effective team leadership and code ownership.",
    },
    {
        "role": "Generalist / Full-Stack Engineer",
        "confidence": lambda t: (t["adaptability"] * 0.35 + t["learning_velocity"] * 0.35 + t["creativity"] * 0.3) / 100,
        "reason": "Broad experimentation and high learning velocity across diverse repositories signals a generalist profile comfortable spanning the full stack.",
    },
    {
        "role": "Research / ML Engineer",
        "confidence": lambda t: (t["analytical"] * 0.45 + t["creativity"] * 0.3 + t["persistence_index_proxy"] * 0.25) / 100
        if "persistence_index_proxy" in t else (t["analytical"] * 0.5 + t["creativity"] * 0.5) / 100,
        "reason": "Combination of high analytical depth with creativity and tolerance for ambiguity aligns with research-driven or ML engineering roles.",
    },
]


def predict_role(traits: Dict[str, float]) -> Dict[str, Any]:
    """Return best-fit engineering role with confidence and explanation."""
    best = max(_ROLES, key=lambda r: r["confidence"](traits))
    score = best["confidence"](traits)
    return {
        "role": best["role"],
        "reason": best["reason"],
        "confidence": round(min(score * 100, 99.0), 1),
    }


# ─────────────────────────────────────────────────────────────
# 3. WORK STYLE PREDICTION
# ─────────────────────────────────────────────────────────────

_STYLES = [
    {
        "style": "Deep Work Specialist",
        "detail": "You work best in low-interruption environments with long unbroken problem-solving sessions. "
                  "Avoid meeting-heavy cultures. Thrive in async-first teams.",
        "match": lambda m: m.get("night_commit_ratio", 0) > 0.4
                           or m.get("avg_commit_hour", 12) > 20
                           or m.get("avg_commit_hour", 12) < 6,
    },
    {
        "style": "Sprint-and-Surge Executor",
        "detail": "You produce in high-intensity bursts followed by recovery periods. "
                  "Well-suited for project-driven work with clear deadlines and delivery sprints.",
        "match": lambda m: m.get("burst_session_count", 0) > 3
                           and m.get("commit_consistency", 0) > 86400,
    },
    {
        "style": "Steady-Cadence Builder",
        "detail": "You maintain consistent daily output with low variance. "
                  "Ideal for long-horizon projects, platform maintenance, and reliability engineering.",
        "match": lambda m: m.get("commit_consistency", 9999) < 43200
                           and m.get("total_commits", 0) > 10,
    },
    {
        "style": "Collaborative Momentum Driver",
        "detail": "You gain energy from team interaction and async discussion. "
                  "Perform best in collaborative environments with regular code review and pair work.",
        "match": lambda m: m.get("collaboration_index", 0) > 0.3,
    },
]

_DEFAULT_STYLE = {
    "style": "Independent Explorer",
    "detail": "Self-directed work style with broad curiosity. "
              "Performs well with autonomy, minimal supervision, and space to experiment.",
}


def predict_work_style(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Return work style label + behaviorally grounded description."""
    for s in _STYLES:
        if s["match"](metrics):
            return {"style": s["style"], "detail": s["detail"]}
    return _DEFAULT_STYLE
