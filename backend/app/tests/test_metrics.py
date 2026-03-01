from app.feature_engineering.metrics import commit_consistency_score, focus_depth_score


def test_commit_consistency_score():
    class Dummy:
        def __init__(self, ts):
            self.author_date = ts

    commits = [Dummy(__import__("datetime").datetime(2024, 1, 1)), Dummy(__import__("datetime").datetime(2024, 1, 2))]
    score = commit_consistency_score(commits)
    assert score >= 0


def test_focus_depth_score():
    class Dummy:
        def __init__(self, total):
            self.total_changes = total

    commits = [Dummy(10), Dummy(20)]
    assert focus_depth_score(commits) == 15
