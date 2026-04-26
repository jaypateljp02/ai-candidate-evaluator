"""
ML Clustering Module
Uses K-Means to group candidates into tiers based on their
evaluation features from resume and video analysis.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Tier labels mapped by cluster performance
TIER_LABELS = {
    "high": "Strong Hire",
    "mid": "Potential",
    "low": "Needs Review"
}

TIER_COLORS = {
    "Strong Hire": "#27ae60",
    "Potential": "#f39c12",
    "Needs Review": "#e74c3c"
}

TIER_EMOJIS = {
    "Strong Hire": "🟢",
    "Potential": "🟡",
    "Needs Review": "🔴"
}


def build_feature_matrix(candidates):
    """Build a numeric feature matrix from candidate evaluation data.

    Features used:
        - resume_score (0-100)
        - video_score (0-100)
        - experience_years
        - skills_count
        - sentiment_compound (-1 to 1)

    Args:
        candidates: List of ranked candidate dicts

    Returns:
        tuple: (DataFrame of features, list of candidate names)
    """
    features = []
    names = []

    for c in candidates:
        features.append({
            "resume_score": float(c.get("resume_score", 0)),
            "video_score": float(c.get("video_score", 0)),
            "experience_years": float(c.get("experience_years", 0)),
            "skills_count": float(c.get("skills_count", 0)),
            "sentiment_compound": float(c.get("sentiment_compound", 0.0)),
        })
        names.append(c.get("name", "Unknown"))

    df = pd.DataFrame(features)
    return df, names


def cluster_candidates(candidates, n_clusters=3):
    """Apply K-Means clustering to group candidates into tiers.

    Automatically adjusts n_clusters if there are fewer candidates
    than requested clusters. Labels clusters based on average
    final score within each cluster.

    Args:
        candidates: List of ranked candidate dicts
        n_clusters: Number of clusters (default: 3)

    Returns:
        list: Same candidates list with 'tier' and 'cluster_id' added
    """
    if not candidates:
        return candidates

    # Need at least 2 candidates and can't have more clusters than candidates
    n_clusters = min(n_clusters, len(candidates))
    if n_clusters < 2:
        # Only 1 candidate — assign best tier
        candidates[0]["tier"] = TIER_LABELS["high"]
        candidates[0]["cluster_id"] = 0
        return candidates

    # Build feature matrix
    feature_df, names = build_feature_matrix(candidates)

    # Standardize features (important for K-Means)
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_df)

    # Run K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled_features)

    # Calculate average final score per cluster to determine tier ranking
    cluster_scores = {}
    for i, c in enumerate(candidates):
        cid = cluster_labels[i]
        if cid not in cluster_scores:
            cluster_scores[cid] = []
        cluster_scores[cid].append(c.get("final_score", 0))

    cluster_avg = {cid: np.mean(scores) for cid, scores in cluster_scores.items()}

    # Rank clusters by average score: highest → "Strong Hire", lowest → "Needs Review"
    sorted_clusters = sorted(cluster_avg.items(), key=lambda x: x[1], reverse=True)

    tier_keys = ["high", "mid", "low"]
    cluster_to_tier = {}
    for idx, (cid, avg) in enumerate(sorted_clusters):
        tier_key = tier_keys[min(idx, len(tier_keys) - 1)]
        cluster_to_tier[cid] = TIER_LABELS[tier_key]

    # Assign tier labels to candidates
    for i, c in enumerate(candidates):
        c["cluster_id"] = int(cluster_labels[i])
        c["tier"] = cluster_to_tier[cluster_labels[i]]

    return candidates


def get_cluster_summary(candidates):
    """Get summary statistics per cluster/tier.

    Returns:
        dict: tier_name → { count, avg_score, avg_resume, avg_video }
    """
    summary = {}

    for c in candidates:
        tier = c.get("tier", "Unknown")
        if tier not in summary:
            summary[tier] = {
                "count": 0,
                "total_final": 0,
                "total_resume": 0,
                "total_video": 0
            }
        summary[tier]["count"] += 1
        summary[tier]["total_final"] += c.get("final_score", 0)
        summary[tier]["total_resume"] += c.get("resume_score", 0)
        summary[tier]["total_video"] += c.get("video_score", 0)

    # Calculate averages
    for tier, data in summary.items():
        n = data["count"]
        data["avg_final"] = round(data["total_final"] / n, 1)
        data["avg_resume"] = round(data["total_resume"] / n, 1)
        data["avg_video"] = round(data["total_video"] / n, 1)

    return summary
