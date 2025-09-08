
from typing import Any, Dict, Optional, List
import os, json, psycopg
import logging

logger = logging.getLogger(__name__)

class WorldCoreDAL:
    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.environ.get("POSTGRES_DSN")
        if not self.dsn: 
            raise RuntimeError("POSTGRES_DSN is required")
    
    def _get_connection(self):
        """Get database connection with proper error handling"""
        try:
            return psycopg.connect(self.dsn)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise RuntimeError(f"Database connection failed: {e}")
    
    def propose(self, entity: Dict[str, Any], cid: str) -> str:
        """Store a proposal for later approval"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Check if proposal already exists
                    cur.execute("SELECT cid FROM proposals WHERE cid=%s", (cid,))
                    if cur.fetchone():
                        logger.info(f"Proposal {cid} already exists")
                        return cid
                    
                    # Insert new proposal
                    cur.execute(
                        "INSERT INTO proposals(cid, payload) VALUES (%s, %s)", 
                        (cid, json.dumps(entity))
                    )
                conn.commit()
                logger.info(f"Proposal {cid} created for entity {entity.get('id')}")
                return cid
        except Exception as e:
            logger.error(f"Failed to create proposal {cid}: {e}")
            raise RuntimeError(f"Failed to create proposal: {e}")
    
    def approve(self, cid: str) -> Dict[str, Any]:
        """Approve a proposal by CID (idempotent)"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Check if proposal exists
                    cur.execute("SELECT payload FROM proposals WHERE cid=%s", (cid,))
                    row = cur.fetchone()
                    
                    if not row:
                        # Check if already approved
                        cur.execute("SELECT id, canon_version FROM entities WHERE cid=%s", (cid,))
                        e = cur.fetchone()
                        if not e: 
                            return {"id": None, "version": 0}
                        return {"id": e[0], "version": e[1]}
                    
                    # Process approval
                    payload = row[0]
                    eid = payload["id"]
                    
                    # Insert/update entity in canon
                    cur.execute("""
                        INSERT INTO entities(id, cid, type, name, status, traits, world_id, canon_version)
                        VALUES (%s, %s, %s, %s, 'CANON', %s, %s, 1)
                        ON CONFLICT (id) DO UPDATE SET 
                            status='CANON', 
                            cid=%s,
                            canon_version=entities.canon_version + 1,
                            updated_at=NOW()
                        RETURNING canon_version
                    """, (
                        eid, cid, payload["type"], payload["name"], 
                        json.dumps(payload.get("traits", {})), 
                        payload.get("world_id"),
                        cid
                    ))
                    
                    version_row = cur.fetchone()
                    version = version_row[0] if version_row else 1
                    
                    # Remove proposal after approval
                    cur.execute("DELETE FROM proposals WHERE cid=%s", (cid,))
                
                conn.commit()
                logger.info(f"Proposal {cid} approved for entity {eid}")
                return {"id": eid, "version": version}
                
        except Exception as e:
            logger.error(f"Failed to approve proposal {cid}: {e}")
            raise RuntimeError(f"Failed to approve proposal: {e}")
    
    def get_canon(self, id: str) -> Optional[Dict[str, Any]]:
        """Get canonical entity by ID"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, cid, type, name, status, traits, world_id, canon_version, created_at, updated_at
                        FROM entities WHERE id=%s
                    """, (id,))
                    row = cur.fetchone()
                    
                    if not row: 
                        return None
                    
                    return {
                        "entity": {
                            "id": row[0],
                            "cid": row[1], 
                            "type": row[2],
                            "name": row[3],
                            "status": row[4],
                            "traits": row[5],
                            "world_id": row[6]
                        }, 
                        "canon_version": row[7],
                        "created_at": row[8].isoformat() if row[8] else None,
                        "updated_at": row[9].isoformat() if row[9] else None
                    }
        except Exception as e:
            logger.error(f"Failed to retrieve entity {id}: {e}")
            raise RuntimeError(f"Failed to retrieve entity: {e}")
    
    def graph(self, world_id: Optional[str] = None, q: Optional[str] = None) -> Dict[str, Any]:
        """Get entity graph with optional filtering"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Build query based on filters
                    if world_id and q:
                        cur.execute("""
                            SELECT id, type, name, status, world_id 
                            FROM entities 
                            WHERE world_id=%s AND (name ILIKE %s OR id ILIKE %s)
                        """, (world_id, f"%{q}%", f"%{q}%"))
                    elif world_id:
                        cur.execute("SELECT id, type, name, status, world_id FROM entities WHERE world_id=%s", (world_id,))
                    elif q:
                        cur.execute("""
                            SELECT id, type, name, status, world_id 
                            FROM entities 
                            WHERE name ILIKE %s OR id ILIKE %s
                        """, (f"%{q}%", f"%{q}%"))
                    else:
                        cur.execute("SELECT id, type, name, status, world_id FROM entities")
                    
                    rows = cur.fetchall()
                    
                    # Build graph structure
                    nodes = []
                    edges = []
                    
                    for row in rows:
                        nodes.append({
                            "id": row[0],
                            "type": row[1], 
                            "label": row[2],
                            "status": row[3],
                            "world_id": row[4]
                        })
                        
                        # Add edges for world relationships
                        if row[4] and row[4] != row[0]:  # Don't self-reference
                            edges.append({
                                "from": row[4],
                                "to": row[0],
                                "type": "contains"
                            })
                    
                    return {
                        "nodes": nodes,
                        "edges": edges,
                        "total_nodes": len(nodes),
                        "total_edges": len(edges)
                    }
                    
        except Exception as e:
            logger.error(f"Failed to retrieve graph: {e}")
            raise RuntimeError(f"Failed to retrieve graph: {e}")
    
    def get_proposals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending proposals"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT cid, payload, created_at 
                        FROM proposals 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (limit,))
                    rows = cur.fetchall()
                    
                    return [
                        {
                            "cid": row[0],
                            "entity": row[1],
                            "created_at": row[2].isoformat() if row[2] else None
                        }
                        for row in rows
                    ]
        except Exception as e:
            logger.error(f"Failed to retrieve proposals: {e}")
            raise RuntimeError(f"Failed to retrieve proposals: {e}")
