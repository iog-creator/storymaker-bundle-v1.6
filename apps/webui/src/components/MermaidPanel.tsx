import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

// Minimal Mermaid renderer with error fallback
export default function MermaidPanel({ code }: { code: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });
        const { svg } = await mermaid.render("pf-lg-diagram", code);
        if (active && ref.current) ref.current.innerHTML = svg;
      } catch (e: any) {
        setErr(e?.message ?? String(e));
      }
    })();
    return () => { active = false; };
  }, [code]);
  return (
    <div className="rounded-2xl border p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold">PF→LangGraph Diagram</h3>
        {err && <span className="text-xs text-red-600">Mermaid error: {err}</span>}
      </div>
      <div ref={ref} className="overflow-auto" />
    </div>
  );
}
