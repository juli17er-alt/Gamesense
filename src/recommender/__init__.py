"""Recommender module for GameSense."""
try:
    from .engine import ContentBasedRecommender, CollaborativeFilteringRecommender
    from .explainer import RecommendationExplainer
except ImportError:
    from src.recommender.engine import ContentBasedRecommender, CollaborativeFilteringRecommender
    from src.recommender.explainer import RecommendationExplainer

__all__ = ["ContentBasedRecommender", "CollaborativeFilteringRecommender", "RecommendationExplainer"]
