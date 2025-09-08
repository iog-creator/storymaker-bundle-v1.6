
from typing import List, Dict, Set, Tuple
def compute_promise_payoff(cards: List[Dict]) -> Dict[str, List[str]]:
    promised: Set[str] = set(); paid: Set[str] = set()
    for c in cards:
        for p in c.get("promises_made", []) or []: promised.add(p.lower().strip())
        for p in c.get("promises_paid", []) or []: paid.add(p.lower().strip())
    return {"orphans": sorted(list(promised - paid)), "extraneous": sorted(list(paid - promised))}
def trope_budget_ok(text: str, banned: List[str], max_per_1k: int) -> Tuple[bool, Dict[str,int]]:
    t = text.lower(); counts: Dict[str,int] = {}
    for token in banned:
        c = t.count(token.lower())
        if c: counts[token] = c
    words = max(1, len(t.split()))
    per_1k = sum(counts.values()) * 1000 / words
    return per_1k <= max_per_1k, counts
