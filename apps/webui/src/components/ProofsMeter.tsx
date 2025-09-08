import React from "react";
import Tile from "./Tile";
import { fetchProofsCount } from "../lib/api";

export default function ProofsMeter() {
  const [count, setCount] = React.useState<number | null>(null);

  React.useEffect(() => {
    (async () => { setCount(await fetchProofsCount()); })();
  }, []);

  return (
    <Tile title="Proofs">
      <div className="text-3xl font-semibold">{count ?? "—"}</div>
      <div className="text-xs text-zinc-400 mt-1">
        {count === null ? "Worldcore proofs count endpoint not found; using placeholder." : "Total JSON envelopes"}
      </div>
    </Tile>
  );
}
