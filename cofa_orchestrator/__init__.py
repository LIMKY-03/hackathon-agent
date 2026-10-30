"""CofA hackathon task orchestration for the in-platform Codex CLI."""

from .policy import ALLOWED_MODELS
from .spec import TaskSpec

__all__ = ["ALLOWED_MODELS", "TaskSpec"]
__version__ = "0.1.0"

