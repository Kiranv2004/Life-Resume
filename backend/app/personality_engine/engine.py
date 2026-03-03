from __future__ import annotations
import math
from typing import Any, Dict
import numpy as np

from app.personality_engine.reasoning import compute_reasoning, predict_role, predict_work_style


# ─── Sigmoid helper (same as in metrics.py) ──────────────────────────────────
def _sig(x: float, mid: float, steep: float = 1.0) -> float:
    """Logistic curve normalised to 0–100."""
    try:
        return 100.0 / (1.0 + math.exp(-steep * (x - mid)))
    except OverflowError:
        return 0.0 if x < mid else 100.0


def rule_based_scores(m: Dict[str, float]) -> Dict[str, float]:
    """
    Convert raw metrics into 0–100 trait scores using sigmoid curves.
    Each sigmoid is calibrated so typical developer values map to ~40-60
    and exceptional values push toward 80-100.
    """
    # --- Analytical ---
    # complexity_handling: typical 0.5–3, exceptional 5+
    # avg_files_per_commit: more files = more complex changes
    cx = m.get("complexity_handling", 0)
    files = m.get("avg_files_per_commit", 1)
    analytical = _sig(cx, 2.0, 1.2) * 0.6 + _sig(files, 4, 0.5) * 0.4

    # --- Creativity ---
    # experimentation_index (0–1): 0.3 = typical, 0.6+ = high
    # language_diversity: more langs = more creative
    exp = m.get("experimentation_index", 0)
    lang_div = m.get("language_diversity", 1)
    # Softer sigmoid so 94% exp doesn't instantly hit 100
    creativity = _sig(exp, 0.4, 5.0) * 0.5 + _sig(lang_div, 4, 0.6) * 0.5

    # --- Discipline ---
    # commit_consistency (pstdev in seconds): lower = more disciplined
    # Use log scale: 12h=43200 → high discipline, 7d=604800 → low, 30d+ → very low
    # active_days_ratio: higher = more disciplined
    cons_raw = m.get("commit_consistency", 86400)
    active = m.get("active_days_ratio", 0.1)
    total_commits = m.get("total_commits", 0)
    # Not enough data → can't infer discipline
    if total_commits < 5:
        discipline = max(5.0, total_commits * 3.0)
    else:
        # Log-scale inversion: discipline drops as stddev grows
        if cons_raw <= 0:
            discipline_from_cons = 85.0
        else:
            # log10(43200)≈4.6 → 85, log10(172800)≈5.2 → 55, log10(2772000)≈6.4 → 20
            log_cons = math.log10(max(cons_raw, 1))
            discipline_from_cons = max(5.0, min(95.0, 160 - 22 * log_cons))
        # Active days boost (0.03→low, 0.3→moderate, 0.7→high)
        discipline_from_active = _sig(active, 0.15, 12.0)
        # Commit volume boost: more commits = more disciplined baseline
        volume_boost = min(15.0, total_commits * 0.15)
        discipline = max(8.0, discipline_from_cons * 0.4 + discipline_from_active * 0.4 + volume_boost + 5)

    # --- Collaboration ---
    # collaboration_index: typical 0.05–0.3, high 0.5+
    # pull_requests: more = more collaborative
    ci = m.get("collaboration_index", 0)
    prs = m.get("pull_requests", 0)
    total_commits_c = m.get("total_commits", 1)
    # Small floor from commit volume (solo devs still get some credit)
    base_collab = min(10.0, total_commits_c * 0.04)
    collaboration = max(8.0, _sig(ci, 0.1, 12.0) * 0.5 + _sig(prs, 5, 0.4) * 0.35 + base_collab * 0.15 + 3)

    # --- Adaptability ---
    # focus_depth (avg total_changes): more changes = adapting to bigger scope
    # code_churn_ratio: higher churn = more refactoring/adapting
    fd = m.get("focus_depth", 0)
    churn = m.get("code_churn_ratio", 0.3)
    adaptability = _sig(fd, 80, 0.03) * 0.5 + _sig(churn, 0.35, 8.0) * 0.5

    # --- Learning Velocity ---
    # experimentation_index + language_diversity + total_repos
    repos = m.get("total_repos", 1)
    # Softer curves to avoid 100% saturation
    learning_velocity = (
        _sig(exp, 0.35, 6.0) * 0.35
        + _sig(lang_div, 3.5, 0.6) * 0.35
        + _sig(repos, 8, 0.25) * 0.30
    )

    # --- Risk Appetite ---
    # experimentation_index high + burst sessions (intense work)
    bursts = m.get("burst_session_count", 0)
    risk_appetite = _sig(exp, 0.3, 8.0) * 0.5 + _sig(bursts, 3, 0.6) * 0.5

    # --- Stress Stability ---
    # Low persistence_index = stable (few fix/retry commits)
    # pr_merge_ratio high = clean work
    pi = m.get("persistence_index", 0)
    merge = m.get("pr_merge_ratio", 0.5)
    stability_from_pi = 100.0 - _sig(pi, 0.3, 8.0)
    stress_stability = stability_from_pi * 0.5 + _sig(merge, 0.5, 6.0) * 0.5

    return {
        "analytical":        round(analytical, 2),
        "creativity":        round(creativity, 2),
        "discipline":        round(discipline, 2),
        "collaboration":     round(collaboration, 2),
        "adaptability":      round(adaptability, 2),
        "learning_velocity": round(learning_velocity, 2),
        "risk_appetite":     round(risk_appetite, 2),
        "stress_stability":  round(stress_stability, 2),
    }


def _smooth_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Gentle smoothing: pull extreme outliers slightly toward the group mean.
    This prevents one trait dominating at 100 while others cluster near 0.
    Blend factor 0.15 = 85% original + 15% group mean.
    """
    values = list(scores.values())
    group_mean = sum(values) / len(values) if values else 50.0
    blend = 0.15
    return {
        k: round(float(np.clip(v * (1 - blend) + group_mean * blend, 5, 98)), 1)
        for k, v in scores.items()
    }


def infer_personality(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Behavioral inference engine using sigmoid-calibrated scoring.
    Returns traits + reasoning + role + work style.
    """
    base_scores = rule_based_scores(metrics)
    traits = _smooth_scores(base_scores)

    reasoning   = compute_reasoning(traits, metrics)
    role_data   = predict_role(traits)
    style_data  = predict_work_style(metrics)

    return {
        # Core trait scores
        **traits,
        # Interpretability layer
        "reasoning":        reasoning,
        "predicted_role":   role_data["role"],
        "role_reason":      role_data["reason"],
        "role_confidence":  role_data["confidence"],
        "work_style":       style_data["style"],
        "work_style_detail": style_data["detail"],
    }
