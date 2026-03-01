from __future__ import annotations
from typing import Dict
import numpy as np
from sklearn.cluster import KMeans


def rule_based_scores(metrics: Dict[str, float]) -> Dict[str, float]:
    return {
        "analytical": metrics["complexity_handling"] * 10,
        "creativity": metrics["experimentation_index"] * 100,
        "discipline": max(0.0, 100 - metrics["commit_consistency"] / 3600),
        "collaboration": metrics["collaboration_index"] * 50,
        "adaptability": metrics["focus_depth"] / 10,
        "learning_velocity": metrics["experimentation_index"] * 120,
        "risk_appetite": metrics["experimentation_index"] * 80,
        "stress_stability": max(0.0, 100 - metrics["persistence_index"] * 50),
    }


def cluster_adjustment(vector: np.ndarray) -> np.ndarray:
    if len(vector) < 2:
        return vector
    data = np.vstack([vector, vector * 1.05, vector * 0.95])
    kmeans = KMeans(n_clusters=2, n_init=10, random_state=42)
    labels = kmeans.fit_predict(data)
    centroid = kmeans.cluster_centers_[labels[0]]
    return centroid


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    values = np.array(list(scores.values()), dtype=float)
    if values.max() == values.min():
        normalized = np.zeros_like(values)
    else:
        normalized = 100 * (values - values.min()) / (values.max() - values.min())
    return {k: float(np.clip(v, 0, 100)) for k, v in zip(scores.keys(), normalized)}


def infer_personality(metrics: Dict[str, float]) -> Dict[str, float]:
    base_scores = rule_based_scores(metrics)
    vector = np.array(list(base_scores.values()), dtype=float)
    adjusted = cluster_adjustment(vector)
    adjusted_scores = {k: float(v) for k, v in zip(base_scores.keys(), adjusted)}
    return normalize_scores(adjusted_scores)
