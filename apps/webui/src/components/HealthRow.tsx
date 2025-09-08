import React from "react";
import Tile from "./Tile";
import { fetchHealth, WORLDCORE, NARRATIVE, SCREENPLAY, MEDIA, INTERACT } from "../lib/api";

const services = [
  { name: "worldcore", url: `${WORLDCORE}/health` },
  { name: "narrative", url: `${NARRATIVE}/health` },
  { name: "screenplay", url: `${SCREENPLAY}/health` },
  { name: "media", url: `${MEDIA}/health` },
  { name: "interact", url: `${INTERACT}/health` }
];

export default function HealthRow() {
  const [states, setStates] = React.useState<Record<string, boolean>>({});

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      const pairs = await Promise.all(
        services.map(async s => [s.name, (await fetchHealth(s.url)).ok] as const)
      );
      if (!cancelled) {
        setStates(Object.fromEntries(pairs));
      }
    })();
    return () => { cancelled = true; };
  }, []);

  return (
    <Tile title="Services">
      <div className="flex gap-3">
        {services.map(s => {
          const ok = states[s.name];
          const dot = ok === undefined ? "animate-pulse bg-zinc-600" : ok ? "bg-emerald-500" : "bg-rose-500";
          return (
            <div key={s.name} className="flex items-center gap-2">
              <span className={`inline-block h-3 w-3 rounded-full ${dot}`} />
              <span className="text-sm">{s.name}</span>
            </div>
          );
        })}
      </div>
    </Tile>
  );
}
