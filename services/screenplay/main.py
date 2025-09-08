
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.common.envelope import envelope_ok
app = FastAPI(title="StoryMaker Screenplay", version="1.6.0")
class SceneCard(BaseModel):
    slug: str; where: str; who: List[str]; goal: str
    when: Optional[Dict[str,str]] = None
    conflict_or_twist: Optional[str] = None
    value_shift: Dict[str, Any]
class ExportReq(BaseModel):
    cards: List[SceneCard]; format: str
@app.post("/screenplay/export")
def export(req: ExportReq):
    uri = "asset://screenplays/demo/scene.fdx" if req.format == "fdx" else "asset://screenplays/demo/scene.fountain"
    return envelope_ok({"artifact": {"type": req.format, "uri": uri}}, {"actor":"ai"})
