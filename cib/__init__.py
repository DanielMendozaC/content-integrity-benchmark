"""Content Integrity Benchmark for LLM agents."""
from .data import ATTACKS, CLEAN
from .evaluate import evaluate
from .defense import surface_flag, disagree, PROMPT_STD, PROMPT_ORIG
from .providers import extract

__all__ = ["ATTACKS", "CLEAN", "evaluate", "surface_flag", "disagree",
           "PROMPT_STD", "PROMPT_ORIG", "extract"]
__version__ = "0.1.0"
