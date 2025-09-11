import React from "react";
import Tile from "./Tile";
import { WORLDCORE, NARRATIVE } from "../lib/api";

type Envelope<T=any> = { status?: "ok"|"error"; data?: T; error?: any; meta?: any } | any;

// Call the service exactly as implemented today.
// The service expects { world_id, premise, mode } at POST /narrative/outline
async function postOutline(premise: string): Promise<Envelope> {
  const base = NARRATIVE ?? WORLDCORE;       // prefer direct narrative if set
  const url = `${base}/narrative/outline`;   // NOTE: no /api prefix
  const body = { world_id: "default", premise, mode: "hero_journey" };
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  // Service returns a JSON result (not necessarily our "envelope" shape); show it verbatim.
  return r.json();
}

export default function NarrativePanel() {
  const [premise, setPremise] = React.useState("A heist story in a city of mirrors.");
  const [resp, setResp] = React.useState<Envelope | null>(null);
  const [busy, setBusy] = React.useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try { setResp(await postOutline(premise)); }
    finally { setBusy(false); }
  };

  const ok = resp?.status === "ok" && resp?.meta?.provider === "groq";

  return (
    <Tile title="Narrative (live)">
      <form onSubmit={submit} className="space-y-3">
        <textarea
          value={premise}
          onChange={e=>setPremise(e.target.value)}
          className="w-full h-24 rounded-lg bg-zinc-900 border border-zinc-800 p-2 text-sm"
          placeholder="Premise (sent as { world_id, premise, mode:'hero_journey' })"
        />
        <button disabled={busy} className="px-3 py-1.5 rounded-md bg-emerald-600 disabled:opacity-50">
          Generate Outline
        </button>
      </form>

      {resp && (
        <div className="mt-3 rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 text-sm">
          <div className="mb-1 text-zinc-400">envelope:</div>
          <pre className="whitespace-pre-wrap break-words text-xs">
            {JSON.stringify(resp, null, 2)}
          </pre>
          {!ok && <div className="mt-2 text-rose-400">Provider must be "groq" (check narrative service wiring).</div>}
        </div>
      )}
    </Tile>
  );
}
