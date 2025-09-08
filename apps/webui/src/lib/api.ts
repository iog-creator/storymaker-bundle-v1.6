export type Health = { ok: boolean; name: string; detail?: string };
export type ProofsCount = { count: number };

const env = (k: string) => import.meta.env[k] as string | undefined;
const base = (k: string, fallback?: string) => env(k) ?? fallback;

export const WORLDCORE = base("VITE_WORLDCORE_BASE", "http://127.0.0.1:8000");
export const NARRATIVE = base("VITE_NARRATIVE_BASE", "http://127.0.0.1:8001");
export const SCREENPLAY = base("VITE_SCREENPLAY_BASE", "http://127.0.0.1:8002");
export const MEDIA = base("VITE_MEDIA_BASE", "http://127.0.0.1:8003");
export const INTERACT = base("VITE_INTERACT_BASE", "http://127.0.0.1:8004");

export async function fetchHealth(url: string): Promise<Health> {
  try {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) return { ok: false, name: url, detail: `${r.status}` };
    const j = await r.json();
    // Accept either {ok:true} or {status:"ok"} or similar
    const ok = j.ok === true || j.status === "ok";
    return { ok, name: url, detail: ok ? undefined : JSON.stringify(j) };
  } catch (e: any) {
    return { ok: false, name: url, detail: e?.message ?? "error" };
  }
}

export async function fetchProofsCount(): Promise<number | null> {
  const path = base("VITE_PROOFS_COUNT_PATH", "/api/proofs/count")!;
  const url = `${WORLDCORE}${path}`;
  try {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) return null;
    const j = (await r.json()) as ProofsCount;
    return typeof j?.count === "number" ? j.count : null;
  } catch {
    return null; // worldcore may not expose this yet
  }
}
