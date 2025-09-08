
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from services.common.envelope import envelope_ok
app = FastAPI(title="StoryMaker Media", version="1.6.0")
class AudioReq(BaseModel):
    ssml: str; voice: Optional[str] = None
@app.post("/audio/synth")
def audio_synth(req: AudioReq):
    return envelope_ok({"audio": {"uri": "asset://audio/demo/scene.mp3", "duration_sec": 10.5}}, {"actor":"ai"})
class VisualReq(BaseModel):
    prompt: str; anchors: Optional[List[str]] = None
@app.post("/visual/generate")
def visual_generate(req: VisualReq):
    return envelope_ok({"image": {"uri": "asset://images/demo/still.png", "provider": "gemini", "watermark": {"type": "synthid", "present": True}}}, {"actor":"ai"})
