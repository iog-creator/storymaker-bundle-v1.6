
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from services.common.envelope import envelope_ok
from typing import Dict, Any
app = FastAPI(title="StoryMaker Interact", version="1.6.0")
PERSONAS: Dict[str, Dict[str, Any]] = {"ch_elyra":{"pov":"Elyra","invariants":["will not take a bribe"],"location":"Harbor of Lumen"}}
@app.get("/health")
def health(): return envelope_ok({"ok": True}, {"actor":"api"})
@app.websocket("/npc/session")
async def npc_session(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_json({"status":"ok","data":{"persona": PERSONAS.get("ch_elyra")}})
        while True:
            msg = await ws.receive_json()
            text = (msg.get("msg") or "").lower()
            if "unknown" in text or "invent" in text:
                await ws.send_json({"msg":"I cannot assert that. Proposing a draft fact for approval.","propose":{"type":"PROPOSE_FACT","payload":{"text":msg.get("msg")}}})
            else:
                await ws.send_json({"msg":"Captain Rios commands tonight's patrols at dockside and the east gate.","citations":["f_council","p_harbor"]})
    except WebSocketDisconnect:
        return
