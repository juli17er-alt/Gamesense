"""Analysis module for GameSense."""
try:
    from .player_eda import PlayerBehaviorEDA
except ImportError:
    from src.analysis.player_eda import PlayerBehaviorEDA

__all__ = ["PlayerBehaviorEDA"]
