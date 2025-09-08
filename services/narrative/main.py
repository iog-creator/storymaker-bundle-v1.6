
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.common.envelope import envelope_ok
from services.narrative.ledger import compute_promise_payoff, trope_budget_ok
app = FastAPI(title="StoryMaker Narrative", version="1.6.0")
class SceneCard(BaseModel):
    slug: str; where: str; who: List[str]; goal: str
    when: Optional[Dict[str,str]] = None
    conflict_or_twist: Optional[str] = None
    value_shift: Dict[str, Any]
    promises_made: Optional[List[str]] = None
    promises_paid: Optional[List[str]] = None
    canon_refs: Optional[List[str]] = None
class OutlineReq(BaseModel):
    world_id: str; premise: str; mode: str
    constraints: Optional[List[str]] = None
    draft_text: Optional[str] = None
    cards: Optional[List[SceneCard]] = None
@app.post("/narrative/outline")
def outline(req: OutlineReq):
    beats = [{"id":k,"note":v} for k,v in [
        ("YOU","Establish ordinary world"),("NEED","Protagonist lacks something"),("GO","Cross threshold"),
        ("SEARCH","Trials and learning"),("FIND","Revelation"),("TAKE","Costly decision"),
        ("RETURN","Back to world"),("CHANGE","Transformed self"),
    ]]
    ledger = compute_promise_payoff([c.model_dump() for c in (req.cards or [])])
    ok_trope, counts = trope_budget_ok(req.draft_text or "", banned=[
        "chosen one","ancient prophecy","dark lord","it was all a dream","mysterious stranger",
        "forbidden forest","destined to","balance of light and dark","last of their kind","prophecy foretold","bloodline power"
    ], max_per_1k=2)
    issues=[]; 
    if ledger["orphans"]: issues.append({"type":"promise_orphans","items":ledger["orphans"]})
    if not ok_trope: issues.append({"type":"trope_budget","counts":counts})
    return envelope_ok({"beats": beats, "issues": issues, "ledger": ledger}, {"actor":"ai","world_id": req.world_id})
