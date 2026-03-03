"""smrti (advaita-smrti) — non-dual memory for structured knowledge elicitation.

Usage:
    from smrti import Memory

    mem = Memory(".memory")
    task = mem.tasks.create("My task", description="Details...")
    mem.close()

See https://github.com/aaronjohnson/advaita-smrti for full documentation.
"""

__version__ = "0.5.0"

from .memory import (
    Memory,
    IndexDriftError,
    init,
)
from .memory.models import (
    Task,
    Decision,
    Hypothesis,
    Fact,
    Pattern,
    Connection,
    DecaySummary,
    CoherenceFinding,
    CoherenceReport,
)

__all__ = [
    "__version__",
    "Memory",
    "IndexDriftError",
    "init",
    "Task",
    "Decision",
    "Hypothesis",
    "Fact",
    "Pattern",
    "Connection",
    "DecaySummary",
    "CoherenceFinding",
    "CoherenceReport",
]
