
from typing import Any, Dict, Optional
import os, json, psycopg
class WorldCoreDAL:
    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.environ.get("POSTGRES_DSN")
        if not self.dsn: raise RuntimeError("POSTGRES_DSN is required")
    def propose(self, entity: Dict[str, Any], cid: str) -> str:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO proposals(cid, payload) VALUES (%s, %s) ON CONFLICT DO NOTHING", (cid, json.dumps(entity)))
            conn.commit()
        return cid
    def approve(self, cid: str) -> Dict[str, Any]:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT payload FROM proposals WHERE cid=%s", (cid,))
                row = cur.fetchone()
                if not row:
                    cur.execute("SELECT id, canon_version FROM entities WHERE cid=%s", (cid,))
                    e = cur.fetchone()
                    if not e: return {"id": None, "version": 0}
                    return {"id": e[0], "version": e[1]}
                payload = row[0]; eid = payload["id"]
                cur.execute("""
                    INSERT INTO entities(id, cid, type, name, status, traits, world_id)
                    VALUES (%s,%s,%s,%s,'CANON',%s,%s)
                    ON CONFLICT (id) DO UPDATE SET status='CANON', updated_at=NOW()
                """, (eid, cid, payload["type"], payload["name"], json.dumps(payload.get("traits",{})), payload.get("world_id")))
            conn.commit()
        return {"id": eid, "version": 1}
    def get_canon(self, id: str):
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, cid, type, name, status, traits, world_id, canon_version FROM entities WHERE id=%s", (id,))
                row = cur.fetchone()
                if not row: return None
                return {"entity": {"id":row[0],"cid":row[1],"type":row[2],"name":row[3],"status":row[4],"traits":row[5],"world_id":row[6]}, "canon_version": row[7]}
    def graph(self, world_id: Optional[str]=None, q: Optional[str]=None):
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                if world_id: cur.execute("SELECT id, type, name, status FROM entities WHERE world_id=%s", (world_id,))
                else: cur.execute("SELECT id, type, name, status FROM entities")
                rows = cur.fetchall()
        return {"nodes": [{"id": r[0], "type": r[1], "label": r[2], "status": r[3]} for r in rows], "edges": []}
