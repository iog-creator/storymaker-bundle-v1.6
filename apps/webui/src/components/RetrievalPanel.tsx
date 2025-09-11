import React from "react";
import Tile from "./Tile";
import { WORLDCORE } from "../lib/api";

const ENABLED = (import.meta.env.VITE_ENABLE_RETRIEVAL ?? "false") === "true";

export default function RetrievalPanel() {
  if (!ENABLED) {
    return (
      <Tile title="Retrieval (LM Studio)">
        <div className="text-sm text-zinc-400">
          Disabled (endpoints not present). Set <code>VITE_ENABLE_RETRIEVAL=true</code> in
          <code> apps/webui/.env.local</code> after implementing:
          <ul className="list-disc pl-6 mt-2">
            <li>POST {WORLDCORE}/api/search/embed</li>
            <li>POST {WORLDCORE}/api/search/rerank</li>
          </ul>
        </div>
      </Tile>
    );
  }
  return (
    <Tile title="Retrieval (LM Studio)">
      <div className="text-sm text-green-400">
        ✅ Retrieval endpoints active
      </div>
      <div className="text-xs text-zinc-400 mt-2">
        Embed: {WORLDCORE}/api/search/embed<br/>
        Rerank: {WORLDCORE}/api/search/rerank
      </div>
    </Tile>
  );
}
