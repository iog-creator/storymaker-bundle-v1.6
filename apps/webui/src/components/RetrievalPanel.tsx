import React from "react";
import Tile from "./Tile";
import { WORLDCORE } from "../lib/api";
type Env<T=any> = { status:"ok"|"error"; data?:T; error?:any; meta?:any };

async function call<T=any>(path: string, payload: unknown): Promise<Env<T>> {
  const url = `${WORLDCORE}${path}`;
  const r = await fetch(url, { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
  return r.json();
}

export default function RetrievalPanel() {
  const [doc, setDoc] = React.useState("A short document about basalt-fiber hulls and polycarbonate underbelly.");
  const [q, setQ] = React.useState("What is the hull made of?");
  const [embedEnv, setEmbedEnv] = React.useState<Env | null>(null);
  const [searchEnv, setSearchEnv] = React.useState<Env | null>(null);
  const [busy, setBusy] = React.useState(false);

  const doEmbed = async () => {
    setBusy(true);
    try { setEmbedEnv(await call("/api/search/embed", { text: doc })); }
    finally { setBusy(false); }
  };
  const doSearch = async () => {
    setBusy(true);
    try { setSearchEnv(await call("/api/search/rerank", { query: q, k: 5 })); }
    finally { setBusy(false); }
  };

  return (
    <Tile title="Retrieval (LM Studio)">
      <div className="grid gap-3">
        <textarea className="w-full h-24 rounded-lg bg-zinc-900 border border-zinc-800 p-2 text-sm"
          value={doc} onChange={e=>setDoc(e.target.value)} placeholder="Document text (embedded server-side)" />
        <button onClick={doEmbed} disabled={busy} className="px-3 py-1.5 rounded-md bg-sky-600 disabled:opacity-50">Embed</button>

        <input className="w-full rounded-lg bg-zinc-900 border border-zinc-800 p-2 text-sm"
          value={q} onChange={e=>setQ(e.target.value)} placeholder="Query" />
        <button onClick={doSearch} disabled={busy} className="px-3 py-1.5 rounded-md bg-violet-600 disabled:opacity-50">Search + Rerank</button>

        {embedEnv && (<pre className="text-xs rounded-lg border border-zinc-800 bg-zinc-900/50 p-2 overflow-auto">
          {JSON.stringify(embedEnv, null, 2)}
        </pre>)}
        {searchEnv && (<pre className="text-xs rounded-lg border border-zinc-800 bg-zinc-900/50 p-2 overflow-auto">
          {JSON.stringify(searchEnv, null, 2)}
        </pre>)}
      </div>
    </Tile>
  );
}
