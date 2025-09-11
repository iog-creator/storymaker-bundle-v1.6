import React from "react";
import * as d3 from "d3-force";

type Node = { id: string; label?: string; type?: string; x?: number; y?: number; vx?: number; vy?: number };
type Edge = { source: string; target: string; relation?: string };
type Graph = { nodes: Node[]; edges: Edge[] };

const toneByType: Record<string, string> = {
  Characters: "#22c55e",
  Places: "#60a5fa",
  Factions: "#f59e0b",
  Cultures: "#a78bfa",
  Items: "#f97316",
  Events: "#e879f9",
};

export default function GraphPanel({ worldcore }: { worldcore: string }) {
  const [graph, setGraph] = React.useState<Graph | null>(null);
  const [err, setErr] = React.useState<string | null>(null);
  const ref = React.useRef<SVGSVGElement>(null);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`${worldcore}/graph`);
        if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
        const j = (await r.json()) as any;
        const g: Graph = { nodes: j.nodes ?? [], edges: (j.edges ?? []).map((e:any)=>({ source: e.from ?? e.source, target: e.to ?? e.target, relation: e.type ?? e.relation })) };
        if (!cancelled) setGraph(g);
      } catch (e: any) {
        if (!cancelled) setErr(e?.message ?? "Graph unavailable");
      }
    })();
    return () => { cancelled = true; };
  }, [worldcore]);

  React.useEffect(() => {
    if (!graph || !ref.current) return;
    const sim = d3.forceSimulation<Node>(graph.nodes)
      .force("link", d3.forceLink<Node, any>(graph.edges as any).id(d=>d.id).distance(100).strength(0.25))
      .force("charge", d3.forceManyBody().strength(-140))
      .force("center", d3.forceCenter(400/2, 320/2))
      .stop();
    for (let i=0;i<150;i++) sim.tick();

    const svg = ref.current; while (svg.firstChild) svg.removeChild(svg.firstChild);
    const gEdges = document.createElementNS("http://www.w3.org/2000/svg","g");
    const gNodes = document.createElementNS("http://www.w3.org/2000/svg","g");
    svg.appendChild(gEdges); svg.appendChild(gNodes);
    for (const e of graph.edges){
      const s = graph.nodes.find(n=> n.id === (e as any).source);
      const t = graph.nodes.find(n=> n.id === (e as any).target);
      if (!s || !t) continue;
      const line = document.createElementNS("http://www.w3.org/2000/svg","line");
      line.setAttribute("x1", String(s.x)); line.setAttribute("y1", String(s.y));
      line.setAttribute("x2", String(t.x)); line.setAttribute("y2", String(t.y));
      line.setAttribute("stroke", "#3f3f46"); line.setAttribute("stroke-width", "1");
      gEdges.appendChild(line);
    }
    for (const n of graph.nodes){
      const color = toneByType[n.type ?? ""] ?? (n.type ? "#a1a1aa" : "#94a3b8");
      const circle = document.createElementNS("http://www.w3.org/2000/svg","circle");
      circle.setAttribute("cx", String(n.x)); circle.setAttribute("cy", String(n.y));
      circle.setAttribute("r", "8"); circle.setAttribute("fill", color); circle.setAttribute("fill-opacity", "0.85");
      gNodes.appendChild(circle);
      const label = document.createElementNS("http://www.w3.org/2000/svg","text");
      label.setAttribute("x", String((n.x ?? 0) + 12)); label.setAttribute("y", String((n.y ?? 0) + 4));
      label.setAttribute("font-size", "10"); label.setAttribute("fill", "#e4e4e7");
      label.textContent = n.label ?? n.id; gNodes.appendChild(label);
    }
  }, [graph]);

  return (
    <div className="space-y-2">
      {err && (
        <div className="rounded-lg border border-amber-700/50 bg-amber-900/20 px-3 py-2 text-xs text-amber-300">
          World graph unavailable ({err}). If you’re running without Postgres (`POSTGRES_DSN`), this view will fall back to a stub.
        </div>
      )}
      {!graph && !err && <div className="text-sm text-zinc-500">Loading graph…</div>}
      <svg ref={ref} width={400} height={320} className="w-full rounded-xl border border-zinc-800 bg-zinc-900/50" />
      <div className="flex items-center gap-2 text-[11px] text-zinc-500">
        <span className="inline-block h-2 w-2 rounded-full" style={{background:"#22c55e"}}/> Characters
        <span className="inline-block h-2 w-2 rounded-full" style={{background:"#60a5fa"}}/> Places
        <span className="inline-block h-2 w-2 rounded-full" style={{background:"#f59e0b"}}/> Factions
        <span className="inline-block h-2 w-2 rounded-full" style={{background:"#a78bfa"}}/> Cultures
      </div>
    </div>
  );
}


