import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import "./styles.css";
import QAView from "./components/QAView";
import GraphPanel from "./components/GraphPanel";
import OnboardingHint from "./components/OnboardingHint";
import MermaidPanel from "./components/MermaidPanel";
function ShortcutHint(){
  const [open, setOpen] = React.useState(false);
  React.useEffect(()=>{
    const onKey = (e: KeyboardEvent)=>{ if ((e.ctrlKey || (e as any).metaKey) && e.key.toLowerCase() === "/") setOpen(o=>!o); };
    window.addEventListener("keydown", onKey as any); return ()=> window.removeEventListener("keydown", onKey as any);
  }, []);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/50 grid place-items-center">
      <div className="w-[520px] rounded-2xl border border-zinc-700 bg-zinc-950 p-5">
        <div className="text-sm text-zinc-400 mb-3">Keyboard Shortcuts</div>
        <ul className="text-sm text-zinc-300 space-y-2">
          <li><b>⌘/Ctrl+Enter</b> — Generate Outline</li>
          <li><b>⌘/Ctrl+K</b> — Run QA Checks</li>
          <li><b>Right-click beat</b> — Split into Scene Card</li>
          <li><b>⌘/Ctrl+/</b> — Toggle this help</li>
        </ul>
        <div className="mt-4 text-right">
          <button className="text-xs rounded border border-zinc-700 px-2 py-1" onClick={()=>setOpen(false)}>Close</button>
        </div>
      </div>
    </div>
  );
}

/*
  StoryMaker Studio – v2 (Aligned with the Master Plan)
  -----------------------------------------------------
  ✨ Upgrades over v1:
  - Canon panel: search/filter, quick propose, approve (UI), entity details drawer, status chips
  - Creative flow: structure picker, outline → draggable beats → scene cards (WHO/WHERE/WHEN/GOAL)
  - QA: "Run Checks" button pipes draft to trope & promise/payoff endpoints, visual ledger
  - AI Collab: provider status, tabbed side panel (Status / QA / History), live proofs counter
  - UX: keyboard shortcuts, context menu on beats, optimistic animations

  Drop-in instructions (apps/webui):
  1) npm i @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities framer-motion
  2) Replace App.tsx default export with <StoryMakerStudio />
  3) Ensure env: VITE_WORLDCORE_BASE, VITE_NARRATIVE_BASE, VITE_PROOFS_COUNT_PATH
*/

// ---------- ENV / API helpers ----------
const env = (k: string) => (import.meta as any).env[k] as string | undefined;
const WORLDCORE = env("VITE_WORLDCORE_BASE") ?? "http://127.0.0.1:8000";
const NARRATIVE = env("VITE_NARRATIVE_BASE") ?? "http://127.0.0.1:8001";
const PROOFS_PATH = env("VITE_PROOFS_COUNT_PATH") ?? "/api/proofs/count";

async function getJSON<T = any>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

// ---------- UI primitives ----------
function Pill({ children, tone = "zinc" }: { children: React.ReactNode; tone?: "emerald" | "amber" | "rose" | "zinc" }) {
  const map = {
    emerald: "bg-emerald-900/30 text-emerald-300 border-emerald-700/50",
    amber: "bg-amber-900/30 text-amber-300 border-amber-700/50",
    rose: "bg-rose-900/30 text-rose-300 border-rose-700/50",
    zinc: "bg-zinc-900/30 text-zinc-300 border-zinc-700/50",
  } as const;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium ${map[tone]}`}>
      {children}
    </span>
  );
}

function Card({ title, right, children }: { title: React.ReactNode; right?: React.ReactNode; children?: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/40 shadow">
      <div className="flex items-center justify-between px-4 pt-3 pb-2">
        <div className="text-sm text-zinc-400">{title}</div>
        <div className="text-xs text-zinc-500">{right}</div>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}
function VersionPill(){
  return <span className="rounded-full border border-zinc-700 px-2 py-0.5 text-[11px] text-zinc-300">UI v2</span>;
}
function EnvBanner(){
  const miss:string[] = [];
  const e:any = (import.meta as any).env;
  if (!e.VITE_WORLDCORE_BASE) miss.push("VITE_WORLDCORE_BASE");
  if (!e.VITE_NARRATIVE_BASE) miss.push("VITE_NARRATIVE_BASE");
  if (!e.VITE_PROOFS_COUNT_PATH) miss.push("VITE_PROOFS_COUNT_PATH");
  if (!miss.length) return null;
  return (
    <div className="mx-auto max-w-7xl px-5 pt-3">
      <div className="rounded-lg border border-amber-700/50 bg-amber-900/20 px-3 py-2 text-xs text-amber-300">
        Missing env: {miss.join(", ")}. The UI will still load, but some panels may be limited.
      </div>
    </div>
  );
}

// ---------- Canon Tree (Left panel) ----------
const ENTITY_TYPES = ["Characters", "Places", "Factions", "Cultures", "Items", "Events"] as const;
type EntityType = typeof ENTITY_TYPES[number];

type Entity = { id: string; name: string; type: EntityType; status: "DRAFT" | "CANON"; summary?: string };

type DrawerState = { open: boolean; entity?: Entity };

function CanonTree({ items, onPropose, onApprove }: { items: Entity[]; onPropose(type: EntityType): void; onApprove(id: string): void }) {
  const [filter, setFilter] = React.useState("");
  const [drawer, setDrawer] = React.useState<DrawerState>({ open: false });
  const [scope, setScope] = React.useState<EntityType | "All">("All");

  const filtered = React.useMemo(() => items.filter(e => {
    const inScope = scope === "All" || e.type === scope;
    const match = !filter || e.name.toLowerCase().includes(filter.toLowerCase());
    return inScope && match;
  }), [items, filter, scope]);

  return (
    <Card title={<span>World Entities</span>} right={<span className="text-zinc-500">DRAFT / CANON</span>}>
      <div className="space-y-3">
        <div className="flex gap-2">
          <input value={filter} onChange={e=>setFilter(e.target.value)} placeholder="Search entities..." className="flex-1 rounded-md bg-zinc-950 border border-zinc-800 px-2 py-1 text-sm" />
          <select value={scope} onChange={e=>setScope(e.target.value as any)} className="rounded-md bg-zinc-950 border border-zinc-800 px-2 py-1 text-sm">
            <option>All</option>
            {ENTITY_TYPES.map(t=> <option key={t}>{t}</option>)}
          </select>
        </div>
        {ENTITY_TYPES.map((t) => (
          <div key={t}>
            <div className="mb-2 flex items-center justify-between">
              <div className="font-medium text-sm">{t}</div>
              <button onClick={() => onPropose(t)} className="text-xs px-2 py-1 rounded-md border border-zinc-700 hover:bg-zinc-800">Propose</button>
            </div>
            <ul className="grid grid-cols-1 gap-1">
              {filtered.filter(e=>e.type===t).length === 0 && (
                <li className="text-xs text-zinc-500">No entries</li>
              )}
              {filtered.filter(e=>e.type===t).map((e) => (
                <li key={e.id} className="flex items-center justify-between rounded-md bg-zinc-900/60 px-2 py-1 text-sm border border-zinc-800">
                  <button onClick={()=> setDrawer({ open:true, entity:e })} className="truncate text-left hover:underline">{e.name}</button>
                  <div className="flex items-center gap-2">
                    <Pill tone={e.status === "CANON" ? "emerald" : "amber"}>{e.status}</Pill>
                    {e.status === "DRAFT" && (
                      <button onClick={()=> onApprove(e.id)} className="text-[11px] px-2 py-0.5 rounded border border-emerald-700 text-emerald-300 hover:bg-emerald-900/20">Approve</button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Details Drawer */}
      <AnimatePresence>
        {drawer.open && (
          <motion.div initial={{opacity:0, y:10}} animate={{opacity:1, y:0}} exit={{opacity:0, y:10}}
            className="fixed inset-x-0 bottom-0 z-50 mx-auto max-w-3xl rounded-t-2xl border border-zinc-800 bg-zinc-950 p-5 shadow-2xl">
            <div className="flex items-center justify-between">
              <div className="text-sm text-zinc-400">Entity</div>
              <button className="text-zinc-400 hover:text-zinc-200" onClick={()=> setDrawer({ open:false })}>Close</button>
            </div>
            <div className="mt-2">
              <div className="text-lg font-semibold">{drawer.entity?.name}</div>
              <div className="mt-1 flex gap-2 text-sm">
                <Pill tone="zinc">{drawer.entity?.type}</Pill>
                <Pill tone={drawer.entity?.status === "CANON" ? "emerald" : "amber"}>{drawer.entity?.status}</Pill>
              </div>
              <p className="mt-3 text-sm text-zinc-300 whitespace-pre-wrap">{drawer.entity?.summary ?? "No summary yet."}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}

// ---------- Sortable Beats / Scenes (Center panel) ----------
function SortableRow({ id, children, onContextMenu }: { id: string; children: React.ReactNode; onContextMenu?(e: React.MouseEvent): void }) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });
  const style: React.CSSProperties = { transform: CSS.Transform.toString(transform), transition };
  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners} onContextMenu={onContextMenu}
      className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3 cursor-grab">
      {children}
    </div>
  );
}

// Scene card type for WHO/WHERE/WHEN/GOAL
type Scene = { id: string; who?: string; where?: string; when?: string; goal?: string; text: string };

// ---------- Right panel widgets ----------
function ProviderStatus() {
  const [states, setStates] = React.useState<Record<string, boolean>>({});
  React.useEffect(() => {
    let cancel = false;
    (async () => {
      const pairs: [string, boolean][] = await Promise.all([
        ["worldcore", `${WORLDCORE}/health`],
        ["narrative", `${NARRATIVE}/health`],
        ["screenplay", `${WORLDCORE.replace("8000","8002")}/health`],
        ["media", `${WORLDCORE.replace("8000","8003")}/health`],
        ["interact", `${WORLDCORE.replace("8000","8004")}/health`],
      ].map(async ([k,u]) => {
        try { const j:any = await getJSON(u); const ok = j?.ok || j?.status === "ok" || j?.data?.ok; return [k, !!ok]; }
        catch { return [k,false]; }
      }));
      if (!cancel) setStates(Object.fromEntries(pairs));
    })();
    return () => { cancel = true; };
  }, []);

  const Dot = ({ ok }:{ ok?: boolean }) => (
    <span className={`inline-block h-2.5 w-2.5 rounded-full ${ ok===undefined ? "bg-zinc-600 animate-pulse" : ok ? "bg-emerald-500" : "bg-rose-500"}`}/>
  );

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2 text-sm">
        {Object.entries({ worldcore:0, narrative:0, screenplay:0, media:0, interact:0 }).map(([k]) => (
          <div key={k} className="flex items-center gap-2"><Dot ok={states[k]} /><span>{k}</span></div>
        ))}
      </div>
      <div className="flex gap-2">
        <Pill tone="emerald">Groq • creative</Pill>
        <Pill tone="zinc">LM Studio • QA</Pill>
      </div>
    </div>
  );
}

function ProofsCounter() {
  const [count, setCount] = React.useState<number | null>(null);
  React.useEffect(() => {
    getJSON(`${WORLDCORE}${PROOFS_PATH}`).then((j:any)=> setCount(j?.data?.count ?? null)).catch(()=>setCount(null));
  }, []);
  return (
    <div>
      <div className="text-4xl font-semibold leading-none">{count ?? "—"}</div>
      <div className="text-xs text-zinc-500 mt-1">Total envelopes</div>
    </div>
  );
}

function QAStatus({ qa }:{ qa: { trope?: any; payoff?: any } }){
  const trope = qa.trope; const payoff = qa.payoff;
  return (
    <div className="space-y-3">
      <div>
        <div className="mb-1 text-xs text-zinc-500">Trope Budget</div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3 text-sm">
          {trope ? <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(trope, null, 2)}</pre> : <span className="text-zinc-500">No results yet.</span>}
        </div>
      </div>
      <div>
        <div className="mb-1 text-xs text-zinc-500">Promise / Payoff</div>
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3 text-sm">
          {payoff ? <pre className="text-xs whitespace-pre-wrap break-words">{JSON.stringify(payoff, null, 2)}</pre> : <span className="text-zinc-500">No results yet.</span>}
        </div>
      </div>
    </div>
  );
}

function EnvelopeHistory({ items }:{ items: any[] }){
  async function copy(env:any){ await navigator.clipboard.writeText(JSON.stringify(env, null, 2)); }
  return (
    <div className="space-y-4 max-h-[40vh] overflow-auto pr-1">
      {items.length===0 && <div className="text-sm text-zinc-500">No envelopes yet.</div>}
      {items.map((e,i)=> {
        const provider = e?.meta?.provider ?? "unknown";
        const tone = provider === "groq" ? "emerald" : provider === "lm-studio" ? "zinc" : "rose";
        return (
          <div key={i} className="relative pl-5">
            <div className="absolute left-1 top-2 h-2 w-2 rounded-full bg-emerald-500 data-[zinc=true]:bg-zinc-500 data-[rose=true]:bg-rose-500" data-zinc={tone==="zinc"} data-rose={tone==="rose"} />
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-3">
              <div className="flex items-center gap-2 text-sm text-zinc-300">
                <Pill tone={tone as any}>{provider}</Pill>
                <span className="truncate">{e?.data?.task ?? e?.meta?.check ?? "envelope"}</span>
                <span className="ml-auto text-[11px] text-zinc-500">{e?.meta?.latency_ms ? `${e.meta.latency_ms} ms` : ""}</span>
                <button onClick={()=>copy(e)} className="ml-2 text-[11px] rounded border border-zinc-700 px-2 py-0.5 hover:bg-zinc-800">Copy JSON</button>
              </div>
              <details className="mt-2">
                <summary className="cursor-pointer text-xs text-zinc-400">View payload</summary>
                <pre className="mt-2 whitespace-pre-wrap break-words text-xs text-zinc-300">{JSON.stringify(e, null, 2)}</pre>
              </details>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ---------- Center: Creative Flow ----------
function StructurePicker({ value, onChange }:{ value: string; onChange(v:string):void }){
  const opts = ["Hero's Journey","Harmon 8","Kishotenketsu"];
  return (
    <div className="flex flex-wrap gap-2">
      {opts.map(o=> (
        <button key={o} onClick={()=>onChange(o)}
          className={`px-3 py-1.5 rounded-full border text-sm ${value===o? "border-emerald-600 bg-emerald-900/20 text-emerald-300" : "border-zinc-700 hover:bg-zinc-800"}`}>{o}</button>
      ))}
    </div>
  );
}

function CreativeFlow({ onEnvelope, onQA }:{ onEnvelope(e:any):void; onQA(data:{ trope?: any; payoff?: any }):void }){
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));
  const [structure, setStructure] = React.useState("Hero's Journey");
  const [premise, setPremise] = React.useState("A heist story in a city of mirrors.");
  const [beats, setBeats] = React.useState<{id:string; text:string}[]>([]);
  const [scenes, setScenes] = React.useState<Scene[]>([]);
  const [busy, setBusy] = React.useState(false);
  const [menu, setMenu] = React.useState<{x:number;y:number;id:string}|null>(null);

  React.useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "enter") generateOutline();
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") runChecks();
    };
    window.addEventListener("keydown", onKey); return () => window.removeEventListener("keydown", onKey);
  }, [beats]);

  const onDragEnd = (e: DragEndEvent) => {
    const { active, over } = e; if (!over || active.id === over.id) return;
    const oldIndex = beats.findIndex(b=>b.id===active.id); const newIndex = beats.findIndex(b=>b.id===over.id);
    setBeats((items)=> arrayMove(items, oldIndex, newIndex));
  };

  function toScene(b:{id:string;text:string}): Scene {
    return { id: `s-${b.id}`, text: b.text, who: "", where: "", when: "", goal: "" };
  }

  function toMode(name: string): string {
    if (name === "Hero's Journey") return "hero_journey";
    if (name === "Harmon 8") return "harmon_8";
    return "kishotenketsu";
  }

  async function generateOutline(){
    setBusy(true);
    try {
      const env:any = await getJSON(`${NARRATIVE}/narrative/outline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ world_id: "default", premise, mode: toMode(structure) })
      });
      onEnvelope(env);
      const beatsArr = (env?.data?.beats ?? []) as any[];
      const nextBeats = beatsArr.map((b:any, i:number)=> ({ id: `b${i}`, text: b.description || b.objective || b.note || "" }));
      setBeats(nextBeats);
      setScenes(nextBeats.map(toScene));
    } finally { setBusy(false); }
  }

  async function runChecks(){
    const draft = (beats.length ? beats : scenes).map(x=>("text" in x? (x as any).text : (x as Scene).text)).join("\n");
    const post = (path:string) => getJSON(`${WORLDCORE}${path}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ draft })
    }).catch(()=>null);
    const [trope, payoff] = await Promise.all([
      post("/api/qa/trope-budget"),
      post("/api/qa/promise-payoff"),
    ]);
    onQA({ trope, payoff });
  }

  function onBeatContext(e: React.MouseEvent, id: string){
    e.preventDefault();
    setMenu({ x: e.clientX, y: e.clientY, id });
  }

  function splitToScene(id: string){
    const beat = beats.find(b=> b.id === id); if (!beat) return;
    setScenes((xs)=> [{ id: `s-${id}`, text: beat.text, who: "", where: "", when: "", goal: "" }, ...xs]);
    setMenu(null);
  }

  return (
    <div className="space-y-4">
      <Card title="Story Structure">
        <StructurePicker value={structure} onChange={setStructure} />
      </Card>

      <Card title="Premise">
        <OnboardingHint />
        <textarea
          value={premise}
          onChange={(e)=>setPremise(e.target.value)}
          className="w-full h-28 rounded-xl bg-zinc-900 border border-zinc-800 p-3 text-sm"
          placeholder="Describe your premise..."
        />
        <div className="mt-3 flex gap-2">
          <button onClick={generateOutline} disabled={busy}
            className="px-3 py-1.5 rounded-md bg-emerald-600 text-white disabled:opacity-50">Generate Outline (⌘/Ctrl+Enter)</button>
          <button onClick={runChecks} disabled={!beats.length}
            className="px-3 py-1.5 rounded-md bg-zinc-800 border border-zinc-700">Run Checks (⌘/Ctrl+K)</button>
        </div>
      </Card>

      <Card title="Story Beats" right={<span className="text-zinc-500">drag to reorder • right-click a beat</span>}>
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
          <SortableContext items={beats.map(b=>b.id)} strategy={verticalListSortingStrategy}>
            <div className="grid gap-2">
              <AnimatePresence initial={false}>
                {beats.length===0 && (
                  <motion.div initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="text-sm text-zinc-500">
                    Generate an outline to populate beats.
                  </motion.div>
                )}
                {beats.map((b)=> (
                  <SortableRow key={b.id} id={b.id} onContextMenu={(e)=> onBeatContext(e, b.id)}>
                    <div className="group flex items-start gap-3">
                      <div className="mt-1 h-4 w-1 rounded bg-emerald-500/80 group-hover:bg-emerald-400 transition-colors" />
                      <div className="flex-1">
                        <div className="text-sm whitespace-pre-wrap">{b.text}</div>
                        <div className="mt-1 flex gap-2">
                          <Pill tone="zinc">Beat</Pill>
                          <button className="text-[11px] rounded border border-zinc-700 px-2 py-0.5 hover:bg-zinc-800" onClick={(e)=> onBeatContext(e as any, b.id)}>Actions</button>
                        </div>
                      </div>
                      <div className="opacity-40 group-hover:opacity-100 transition-opacity text-zinc-500 select-none">⋮⋮</div>
                    </div>
                  </SortableRow>
                ))}
              </AnimatePresence>
            </div>
          </SortableContext>
        </DndContext>
        {/* context menu */}
        <AnimatePresence>
          {menu && (
            <motion.ul initial={{opacity:0, scale:0.98}} animate={{opacity:1, scale:1}} exit={{opacity:0, scale:0.98}}
              className="fixed z-50 min-w-[180px] rounded-xl border border-zinc-800 bg-zinc-950 p-1 shadow-xl"
              style={{ left: menu.x, top: menu.y }} onMouseLeave={()=> setMenu(null)}>
              <li>
                <button onClick={()=> splitToScene(menu.id)} className="w-full text-left px-3 py-2 rounded-lg hover:bg-zinc-800 text-sm">Split into Scene Card</button>
              </li>
            </motion.ul>
          )}
        </AnimatePresence>
      </Card>

      <Card title="Scene Cards" right={<span className="text-zinc-500">WHO / WHERE / WHEN / GOAL</span>}>
        <div className="grid gap-2">
          {scenes.length===0 && <div className="text-sm text-zinc-500">Right-click a beat → Split into Scene.</div>}
          {scenes.map(s => (
            <div key={s.id} className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-3">
              <div className="text-sm mb-2 whitespace-pre-wrap">{s.text}</div>
              <div className="grid grid-cols-4 gap-2">
                <input placeholder="WHO" value={s.who} onChange={e=> setScenes(xs=> xs.map(x=> x.id===s.id? { ...x, who:e.target.value }: x))}
                  className="rounded-md bg-zinc-950 border border-zinc-800 px-2 py-1 text-xs" />
                <input placeholder="WHERE" value={s.where} onChange={e=> setScenes(xs=> xs.map(x=> x.id===s.id? { ...x, where:e.target.value }: x))}
                  className="rounded-md bg-zinc-950 border border-zinc-800 px-2 py-1 text-xs" />
                <input placeholder="WHEN" value={s.when} onChange={e=> setScenes(xs=> xs.map(x=> x.id===s.id? { ...x, when:e.target.value }: x))}
                  className="rounded-md bg-zinc-950 border border-zinc-800 px-2 py-1 text-xs" />
                <input placeholder="GOAL" value={s.goal} onChange={e=> setScenes(xs=> xs.map(x=> x.id===s.id? { ...x, goal:e.target.value }: x))}
                  className="rounded-md bg-zinc-950 border border-zinc-800 px-2 py-1 text-xs" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

// ---------- Main Studio Shell ----------
export default function StoryMakerStudio(){
  const [envelopes, setEnvelopes] = React.useState<any[]>([]);
  const [qa, setQA] = React.useState<{ trope?: any; payoff?: any }>({});
  const [entities, setEntities] = React.useState<Entity[]>([
    { id:"c-001", name:"Rhea Voss", type:"Characters", status:"CANON", summary:"A master thief shaped by the City of Mirrors." },
    { id:"p-001", name:"City of Mirrors", type:"Places", status:"CANON", summary:"Labyrinthine alleys, reflective facades, secrets everywhere." },
    { id:"f-001", name:"Glass Syndicate", type:"Factions", status:"DRAFT", summary:"An outfit trading in illusions and surveillance." },
  ]);

  function addEnvelope(e:any){ setEnvelopes((xs)=> [e, ...xs].slice(0, 60)); }
  function propose(type: EntityType){
    const id = `${type[0].toLowerCase()}-${Math.random().toString(36).slice(2,7)}`;
    setEntities((xs)=> [{ id, name:`New ${type} ${id.slice(-3)}`, type, status:"DRAFT" }, ...xs]);
  }
  function approve(id: string){ setEntities(xs=> xs.map(e=> e.id===id ? { ...e, status:"CANON" } : e)); }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="sticky top-0 z-10 border-b border-zinc-900/80 bg-zinc-950/80 backdrop-blur">
        <div className="mx-auto max-w-7xl px-5 py-3 flex items-center gap-3">
          <div className="text-lg font-semibold">StoryMaker Studio</div>
          <div className="ml-auto flex items-center gap-2 text-xs text-zinc-400">
            <VersionPill />
            <Pill tone="emerald">Canon</Pill>
            <Pill tone="amber">Draft</Pill>
            <Pill tone="rose">Warning</Pill>
          </div>
        </div>
      </header>

      <EnvBanner />

      <main className="mx-auto max-w-7xl px-5 py-6 grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Canon */}
        <section className="lg:col-span-3 space-y-4">
          <CanonTree items={entities} onPropose={propose} onApprove={approve} />
        </section>

        {/* Center: Creative Flow */}
        <section className="lg:col-span-6 space-y-4">
          <CreativeFlow onEnvelope={addEnvelope} onQA={setQA} />
          <MermaidPanel code={`graph TB
    subgraph "User Interface Layer"
      UI1["Story Maker Studio<br/>React Frontend"]
      UI2["LangGraph Studio<br/>Interactive Debugger"]
      UI3["HTML Visualizer<br/>Mermaid Diagrams"]
      UI4["Terminal Interface<br/>Makefile Commands"]
    end
    subgraph "Configuration Input"
      CFG1["Promptflow YAML<br/>outline.dag.yaml"]
      CFG2["Environment Variables<br/>.env, NARRATIVE_BASE"]
      CFG3["LangGraph Config<br/>langgraph.json"]
      CFG4["Makefile Targets<br/>graph-generate, graph-e2e"]
    end
    subgraph "Code Generation Pipeline"
      CG1["codegen.py<br/>Template Engine"]
      CG2["Template Expression Parser<br/>inputs, env lookups"]
      CG3["Node Function Generator<br/>HTTP calls, Branch logic"]
      CG4["Graph Builder<br/>StateGraph with edges"]
      CG5["_wrap_node<br/>currying client/env"]
    end
    subgraph "Generated LangGraph Runtime"
      LG1["outline_graph.py"]
      LG2["GraphState<br/>reducers (operator.or_)"]
      LG3["Node Functions<br/>narrative_outline, qa_*"]
      LG4["Branch Logic<br/>decide_gate"]
      LG5["Parallel Merge<br/>node deltas"]
    end
    UI1-->CFG1; UI2-->LG1; UI3-->CFG1; UI4-->CFG4
    CFG1-->CG1-->CG2-->CG3-->CG4-->CG5-->LG1
    LG1-->LG2-->LG3-->LG4-->LG5
  `} />
        </section>

        {/* Right: AI Collaboration */}
        <section className="lg:col-span-3 space-y-4">
          <Card title="Providers"><ProviderStatus /></Card>
          <Card title="QA Feedback"><QAView qa={qa} /></Card>
          <Card title="World Graph (beta)"><GraphPanel worldcore={WORLDCORE} /></Card>
          <Card title="Proofs"><ProofsCounter /></Card>
          <Card title="History"><EnvelopeHistory items={envelopes} /></Card>
        </section>
        
        {/* Keyboard Shortcuts Overlay (toggle with Ctrl+/) */}
        <ShortcutHint />
      </main>
    </div>
  );
}
