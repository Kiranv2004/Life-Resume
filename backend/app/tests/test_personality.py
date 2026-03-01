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
    }
    result = infer_personality(metrics)
    assert all(0 <= v <= 100 for v in result.values())
