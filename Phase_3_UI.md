Heck yes—Phase 2 is sealed. Here are the concrete, paste-ready specs to kick off **Phase 3** cleanly, split into four small PRs you can land one-by-one without breaking your rails.

---

# PR-0031 — Web UI scaffold (`apps/webui`)

### Goal

Spin up a tiny, type-safe React + Vite + Tailwind dashboard that:

* reads API bases from env,
* pings service health endpoints,
* shows a Proofs Meter (count from a configurable endpoint or placeholder).

### File tree

```
apps/webui/
  .env.local.example
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  postcss.config.js
  tailwind.config.js
  src/
    main.tsx
    App.tsx
    styles.css
    lib/api.ts
    components/HealthRow.tsx
    components/Tile.tsx
    components/ProofsMeter.tsx
```

### Files (exact contents)

**`apps/webui/package.json`**

```json
{
  "name": "storymaker-webui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "typecheck": "tsc -b --pretty false"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.47",
    "tailwindcss": "^3.4.10",
    "typescript": "^5.6.2",
    "vite": "^5.4.6"
  }
}
```

**`.env.local.example`**

```bash
# Base for service “worldcore” (status/aggregate).
VITE_WORLDCORE_BASE=http://127.0.0.1:8000
# Optional: direct bases (useful during dev)
VITE_NARRATIVE_BASE=http://127.0.0.1:8001
VITE_SCREENPLAY_BASE=http://127.0.0.1:8002
VITE_MEDIA_BASE=http://127.0.0.1:8003
VITE_INTERACT_BASE=http://127.0.0.1:8004
# Proofs count endpoint (should return { "count": number })
VITE_PROOFS_COUNT_PATH=/api/proofs/count
```

**`tailwind.config.js`**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: []
}
```

**`postcss.config.js`**

```js
export default { plugins: { tailwindcss: {}, autoprefixer: {} } }
```

**`tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023", "DOM"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true,
    "types": []
  },
  "include": ["src"]
}
```

**`vite.config.ts`**

```ts
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
export default defineConfig({ plugins: [react()] })
```

**`index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1.0" />
    <title>StoryMaker UI</title>
  </head>
  <body class="bg-zinc-950 text-zinc-100">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**`src/styles.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**`src/lib/api.ts`**

```ts
export type Health = { ok: boolean; name: string; detail?: string };
export type ProofsCount = { count: number };

const env = (k: string) => import.meta.env[k] as string | undefined;
const base = (k: string, fallback?: string) => env(k) ?? fallback;

export const WORLDCORE = base("VITE_WORLDCORE_BASE", "http://127.0.0.1:8000");
export const NARRATIVE = base("VITE_NARRATIVE_BASE", "http://127.0.0.1:8001");
export const SCREENPLAY = base("VITE_SCREENPLAY_BASE", "http://127.0.0.1:8002");
export const MEDIA = base("VITE_MEDIA_BASE", "http://127.0.0.1:8003");
export const INTERACT = base("VITE_INTERACT_BASE", "http://127.0.0.1:8004");

export async function fetchHealth(url: string): Promise<Health> {
  try {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) return { ok: false, name: url, detail: `${r.status}` };
    const j = await r.json();
    // Accept either {ok:true} or {status:"ok"} or similar
    const ok = j.ok === true || j.status === "ok";
    return { ok, name: url, detail: ok ? undefined : JSON.stringify(j) };
  } catch (e: any) {
    return { ok: false, name: url, detail: e?.message ?? "error" };
  }
}

export async function fetchProofsCount(): Promise<number | null> {
  const path = base("VITE_PROOFS_COUNT_PATH", "/api/proofs/count")!;
  const url = `${WORLDCORE}${path}`;
  try {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) return null;
    const j = (await r.json()) as ProofsCount;
    return typeof j?.count === "number" ? j.count : null;
  } catch {
    return null; // worldcore may not expose this yet
  }
}
```

**`src/components/Tile.tsx`**

```tsx
import React from "react";

export default function Tile(props: { title: string; children?: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-4 shadow">
      <div className="text-sm text-zinc-400 mb-2">{props.title}</div>
      {props.children}
    </div>
  );
}
```

**`src/components/HealthRow.tsx`**

```tsx
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
```

**`src/components/ProofsMeter.tsx`**

```tsx
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
```

**`src/App.tsx`**

```tsx
import React from "react";
import "./styles.css";
import HealthRow from "./components/HealthRow";
import ProofsMeter from "./components/ProofsMeter";

export default function App() {
  return (
    <div className="mx-auto max-w-5xl p-6 space-y-6">
      <h1 className="text-2xl font-semibold">StoryMaker Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2"><HealthRow /></div>
        <ProofsMeter />
      </div>
    </div>
  );
}
```

**`src/main.tsx`**

```tsx
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
```

### Makefile (append)

```make
.PHONY: webui.dev webui.build
webui.dev:
	cd apps/webui && npm ci && npm run dev

webui.build:
	cd apps/webui && npm ci && npm run typecheck && npm run build
```

### Verifier runbook

* `cp apps/webui/.env.local.example apps/webui/.env.local`
* `make webui.build` → succeeds
* `make webui.dev` → browse [http://127.0.0.1:5173](http://127.0.0.1:5173)
* Five health dots reflect your service /health endpoints; proofs meter shows number or “placeholder.”

---

# PR-0032 — Narrative panel (Groq path only)

### Goal

A minimal panel that posts a prompt to your narrative endpoint and renders a **validated envelope** (never raw text).

### Files

**`apps/webui/src/components/NarrativePanel.tsx`**

```tsx
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
```

**Integrate in `src/App.tsx`**

```tsx
// ...
import NarrativePanel from "./components/NarrativePanel";
// ...
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <div className="md:col-span-2 space-y-4">
    <HealthRow />
    <NarrativePanel />
  </div>
  <ProofsMeter />
</div>
```

### Acceptance

* Submit → returns `{status:"ok", data:{...}, meta:{provider:"groq", model:"llama-3.3-70b-versatile"}}` (UI shows full envelope).
* If the endpoint is missing, you get a graceful error in the envelope area (no crashes).

---

# PR-0033 — Embed & Rerank loop (LM Studio path)

### Goal

Prove local retrieval rails: embed text, store locally (in browser for now), query + rerank via your API. (Backend specifics vary; this just hits your endpoints and validates envelopes.)

### Files

**`apps/webui/src/components/RetrievalPanel.tsx`**

```tsx
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
```

**Integrate in `src/App.tsx` (under NarrativePanel)**

```tsx
import RetrievalPanel from "./components/RetrievalPanel";
// ...
<NarrativePanel />
<RetrievalPanel />
```

### Acceptance

* `/api/search/embed` returns envelope with `meta.embedding_dims = 1024`.
* `/api/search/rerank` returns top-K with scores; envelope shown.

*(If your worldcore hasn’t exposed these endpoints yet, the UI still renders; just add them later and it’ll light up.)*

---

# PR-0034 — CI for Web UI

### Files

**`.github/workflows/webui.yml`**

```yaml
name: WebUI
on:
  push:
    paths:
      - "apps/webui/**"
      - ".github/workflows/webui.yml"
  pull_request:
    paths:
      - "apps/webui/**"
      - ".github/workflows/webui.yml"
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Use Node
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          cache-dependency-path: "apps/webui/package.json"
      - name: Install
        working-directory: apps/webui
        run: npm ci
      - name: Typecheck
        working-directory: apps/webui
        run: npm run typecheck
      - name: Build
        working-directory: apps/webui
        run: npm run build
```

*(This CI is independent from your guards; it only builds/types your web app.)*

---

## Optional: tiny proof endpoint (server side)

If/when you want the Proofs Meter wired, expose from worldcore:

* `GET /api/proofs/count` → `{ "count": <int> }` (count of `docs/proofs/agentpm/*.json`)

No UI change needed; it’s already configurable via `VITE_PROOFS_COUNT_PATH`.

---

## One-shot apply

1. Create the files above.
2. `cp apps/webui/.env.local.example apps/webui/.env.local`
3. `make webui.build && make webui.dev`

You’ll see:

* **Services row**: 5 dots, green if your `/health` endpoints return OK.
* **Proofs meter**: a number (if endpoint exists) or a placeholder.
* **Narrative panel**: posts a prompt → envelope renders.
* **Retrieval panel**: embed & rerank calls → envelopes render.

---

