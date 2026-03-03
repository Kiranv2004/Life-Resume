from app.personality_engine.engine import infer_personality


def test_infer_personality():
    metrics = {
        "commit_consistency": 1000,
        "focus_depth": 50,
        "collaboration_index": 0.2,
        "experimentation_index": 0.1,
        "persistence_index": 0.05,
        "complexity_handling": 3.0,
        "pull_requests": 2,
        "total_commits": 10,
        "total_repos": 3,
        "night_commit_ratio": 0.1,
        "avg_commit_hour": 14,
        "burst_session_count": 1,
        "language_diversity": 2,
        "pr_merge_ratio": 0.5,
        "avg_files_per_commit": 3,
        "code_churn_ratio": 0.2,
        "active_days_ratio": 0.3,
    }
    result = infer_personality(metrics)
    trait_keys = ["analytical", "creativity", "discipline", "collaboration",
                  "adaptability", "learning_velocity", "risk_appetite", "stress_stability"]
    for k in trait_keys:
        assert 5 <= result[k] <= 98, f"{k}={result[k]}"
    assert isinstance(result["reasoning"], dict)
    assert len(result["reasoning"]) == 8
    assert result["predicted_role"] != ""
    assert result["work_style"] != ""
