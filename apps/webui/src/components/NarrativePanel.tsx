import React from "react";
import Tile from "./Tile";
import { WORLDCORE, NARRATIVE } from "../lib/api";

type Envelope<T=any> = { status: "ok"|"error"; data?: T; error?: any; meta?: any };

async function postOutline(prompt: string): Promise<Envelope> {
  const base = NARRATIVE ?? WORLDCORE; // prefer direct narrative if provided
  const url = `${base}/api/narrative/outline`;
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });
  return r.json();
}

export default function NarrativePanel() {
  const [prompt, setPrompt] = React.useState("A heist story in a city of mirrors.");
  const [env, setEnv] = React.useState<Envelope | null>(null);
  const [busy, setBusy] = React.useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try { setEnv(await postOutline(prompt)); }
    finally { setBusy(false); }
  };

  const ok = env?.status === "ok";

  return (
    <Tile title="Narrative (Groq)">
      <form onSubmit={submit} className="space-y-3">
        <textarea value={prompt} onChange={e=>setPrompt(e.target.value)}
          className="w-full h-24 rounded-lg bg-zinc-900 border border-zinc-800 p-2 text-sm" />
        <button disabled={busy} className="px-3 py-1.5 rounded-md bg-emerald-600 disabled:opacity-50">Outline</button>
      </form>
      {env && (
        <div className="mt-3 rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 text-sm">
          <div className="mb-1 text-zinc-400">envelope:</div>
          <pre className="whitespace-pre-wrap break-words text-xs">{JSON.stringify(env, null, 2)}</pre>
          {!ok && <div className="mt-2 text-rose-400">Provider must be "groq" in meta.</div>}
        </div>
      )}
    </Tile>
  );
}
