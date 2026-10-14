"""Part E: choose a policy honestly. TODO 10."""
from __future__ import annotations


def choose_policy(table: list[dict], baseline_progress: float, max_loss: float = 0.05):
    """Return the row with the lowest fail_hi among rows that keep at least (1 - max_loss)
    of the baseline's progress; break ties by higher progress. None if no row qualifies.

    Ranking by the UPPER bound, not the point estimate, stops you picking a policy that only looks safe
    because its few test crashes happened not to be drawn.
    """
    threshold = baseline_progress * (1 - max_loss)
    candidates = [row for row in table if row["progress"] >= threshold]
    if not candidates:
        return None
    return min(candidates, key=lambda r: (r["fail_hi"], -r["progress"]))
