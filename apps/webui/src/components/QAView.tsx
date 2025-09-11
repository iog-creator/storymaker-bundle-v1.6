import React from "react";

function Bar({ used = 0, cap = 10 }: { used?: number; cap?: number }) {
  const pct = Math.min(100, Math.round((used / Math.max(1, cap)) * 100));
  const tone = pct < 40 ? "bg-emerald-600" : pct < 80 ? "bg-amber-600" : "bg-rose-600";
  return (
    <div className="h-2 w-full rounded-full bg-zinc-800 overflow-hidden">
      <div className={`h-full ${tone}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function QAView({ qa }: { qa: { trope?: any; payoff?: any } }) {
  const tropeUsed = Number(qa?.trope?.data?.used ?? 0);
  const tropeCap = Number(qa?.trope?.data?.cap ?? 10);
  const tropeNotes: string[] = qa?.trope?.data?.notes ?? [];

  const rows: Array<{ setup?: string; payoff?: string; status?: string }>
    = qa?.payoff?.data?.ledger ?? [];

  return (
    <div className="space-y-4">
      <div>
        <div className="mb-1 text-xs text-zinc-500">Trope Budget</div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-zinc-300">Clichés used</span>
            <span className="text-zinc-400">{tropeUsed} / {tropeCap}</span>
          </div>
          <Bar used={tropeUsed} cap={tropeCap} />
          {tropeNotes?.length > 0 && (
            <ul className="mt-2 list-disc pl-5 text-xs text-zinc-400 space-y-1">
              {tropeNotes.map((n, i) => (<li key={i}>{n}</li>))}
            </ul>
          )}
          {!qa?.trope && (
            <div className="text-sm text-zinc-500">No results yet.</div>
          )}
        </div>
      </div>

      <div>
        <div className="mb-1 text-xs text-zinc-500">Promise / Payoff</div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-2">
          <div className="grid grid-cols-12 text-[11px] text-zinc-500 px-2 py-1">
            <div className="col-span-5">Setup</div>
            <div className="col-span-6">Payoff</div>
            <div className="col-span-1 text-right">OK</div>
          </div>
          <div className="divide-y divide-zinc-800">
            {rows?.length ? rows.map((r, i) => (
              <div key={i} className="grid grid-cols-12 items-start gap-2 px-2 py-2 text-xs">
                <div className="col-span-5 text-zinc-300 whitespace-pre-wrap">{r.setup || "—"}</div>
                <div className="col-span-6 text-zinc-300 whitespace-pre-wrap">{r.payoff || "—"}</div>
                <div className="col-span-1 text-right">
                  <span className={`inline-block h-2 w-2 rounded-full ${r.status === "ok" ? "bg-emerald-500" : "bg-rose-500"}`} />
                </div>
              </div>
            )) : (
              <div className="px-2 py-3 text-sm text-zinc-500">No results yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}






