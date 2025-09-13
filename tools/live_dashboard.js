#!/usr/bin/env node
import fs from "fs";
import path from "path";
import { setTimeout as sleep } from "timers/promises";
import { fileURLToPath } from "url";
import { exec } from "child_process";
import { readFile } from "fs/promises";
import { request } from "undici";
// chokidar removed - using SSE for file watching
import blessed from "blessed";
import contrib from "blessed-contrib";
import * as dotenv from "dotenv";
// EventSource removed - using fast polling instead

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const CONFIG = JSON.parse(fs.readFileSync(path.join(__dirname, "dashboard.config.json"), "utf8"));

// ---------- Load env from common files so "env" tiles are accurate ----------
for (const candidate of [".env", ".env.local", ".env.generated", ".agentpm_workspace/.env.generated"]) {
  const p = path.join(ROOT, candidate);
  if (fs.existsSync(p)) dotenv.config({ path: p });
}

// ---------- Blessed UI ----------
const screen = blessed.screen({ smartCSR: true, title: "Agent Live Grid" });
const grid = new contrib.grid({ rows: 4, cols: 4, screen }); // 4 cols to make room for guidance
const logBox = grid.set(3, 0, 1, 3, contrib.log, { label: "Events" });

// ---------- Guidance Panel ----------
const guidanceBox = grid.set(0, 3, 3, 1, blessed.box, {
  label: " Guidance & Next Actions ",
  border: "line",
  style: { border: { fg: "cyan" } },
  scrollable: true,
  alwaysScroll: true,
  focusable: true,
  keys: true,
  mouse: true,
  padding: { left: 1, right: 1, top: 1, bottom: 1 },
  scrollbar: {
    ch: ' ',
    track: { bg: 'cyan' },
    style: { inverse: true }
  }
});

// Persistent notifications storage
const NOTIF_FILE = path.join(__dirname, ".dashboard_notifications.json");
function loadNotifs() {
  try {
    return JSON.parse(fs.readFileSync(NOTIF_FILE, "utf8"));
  } catch {
    return [];
  }
}
function saveNotifs(list) {
  fs.writeFileSync(NOTIF_FILE, JSON.stringify(list.slice(-50), null, 2));
}
function addNotif(kind, msg) {
  const list = loadNotifs();
  const last = list[list.length-1];
  if (last && last.kind === kind && last.msg === msg) return; // prevent duplicates
  list.push({ kind, msg, ts: new Date().toISOString() });
  saveNotifs(list);
}

function mkBox(r, c, h, w, title) {
  return grid.set(r, c, h, w, blessed.box, {
    label: ` ${title} `,
    border: "line",
    style: { border: { fg: "gray" } },
    scrollable: true,
    alwaysScroll: true,
    focusable: true,
    keys: true,
    mouse: true,
    scrollbar: {
      ch: ' ',
      track: {
        bg: 'cyan'
      },
      style: {
        inverse: true
      }
    }
  });
}

const tiles = [];
function addTile(idx, title) {
  // lay out in 3x3 grid for 8 tiles + events
  const colCount = 3;
  const row = Math.floor(idx / colCount);
  const col = idx % colCount;
  const box = mkBox(row, col, 1, 1, title);
  
  // Add individual key bindings for scrolling
  box.key(["up", "k"], () => {
    box.scroll(-1);
    screen.render();
  });
  box.key(["down", "j"], () => {
    box.scroll(1);
    screen.render();
  });
  box.key(["pageup"], () => {
    box.scroll(-5);
    screen.render();
  });
  box.key(["pagedown"], () => {
    box.scroll(5);
    screen.render();
  });
  box.key(["home"], () => {
    box.setScroll(0);
    screen.render();
  });
  box.key(["end"], () => {
    box.setScroll(box.getScrollHeight());
    screen.render();
  });
  
  tiles.push(box);
  return box;
}

const lastContentByBox = new Map();
function setState(box, { status = "unknown", lines = [], blink = false }) {
  const color =
    status === "ok" ? "green" :
    status === "warn" ? "yellow" :
    status === "busy" ? "cyan" :
    status === "error" ? "red" : "gray";
  box.style.border.fg = color;
  const nextContent = lines.join("\n");
  const prevContent = lastContentByBox.get(box);
  const changed = nextContent !== prevContent;
  lastContentByBox.set(box, nextContent);
  box.setContent(nextContent);
  if (blink && changed) {
    let on = true;
    const int = setInterval(() => {
      try {
        box.style.border.fg = on ? color : "black";
        screen.render();
      } catch (_) { clearInterval(int); }
      on = !on;
    }, 400);
    setTimeout(() => clearInterval(int), 4000);
  }
}

function log(msg) {
  logBox.log(`[${new Date().toLocaleTimeString()}] ${msg}`);
}

// ---------- Guidance System ----------
async function refreshGuidance() {
  try {
    const [lm, groq, ssot, proofs] = await Promise.allSettled([
      fetchJson("http://localhost:8700/api/lm/models?cb=" + Date.now()),
      fetchJson("http://localhost:8700/api/groq/model?cb=" + Date.now()),
      fetchJson("http://localhost:8700/api/ssot/status?cb=" + Date.now()),
      fetchJson("http://localhost:8700/api/proofs/summary?cb=" + Date.now()),
    ]);
    
    const S = { 
      lm: lm.value, 
      groq: groq.value, 
      ssot: ssot.value, 
      proofs: proofs.value 
    };
    
    const guidance = buildGuidance(S);
    guidanceBox.setContent(guidance);
    screen.render();
  } catch (e) {
    guidanceBox.setContent(`Error loading guidance:\n${e.message}`);
    screen.render();
  }
}

function buildGuidance(S) {
  const recs = [];
  
  // LM Studio
  if (S.lm && S.lm.ok) {
    if (!S.lm.chat || !S.lm.embed) {
      recs.push(`{cyan-fg}LM Studio:{/cyan-fg} start ${!S.lm.chat ? 'a chat model' : 'an embed model'}`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Press L for checklist`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Models: qwen3-8b-instruct + qwen3-embedding-0.6b`);
    }
  } else {
    recs.push(`{red-fg}LM Studio:{/red-fg} not reachable or no models`);
    recs.push(`  {yellow-fg}→{/yellow-fg} Press L for checklist`);
    recs.push(`  {yellow-fg}→{/yellow-fg} Start LM Studio at http://127.0.0.1:1234`);
  }
  
  // Groq
  if (S.groq && !S.groq.ok) {
    if (Array.isArray(S.groq.missing) && S.groq.missing.length) {
      recs.push(`{red-fg}Groq:{/red-fg} missing ${S.groq.missing.join(", ")}`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Press G for checklist`);
      recs.push(`  {yellow-fg}→{/yellow-fg} export GROQ_API_KEY=your_key_here`);
    } else {
      recs.push(`{red-fg}Groq:{/red-fg} ${S.groq.error || "model not available"}`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Press G for checklist`);
      recs.push(`  {yellow-fg}→{/yellow-fg} export GROQ_MODEL=llama-3.3-70b-versatile`);
    }
  }
  
  // SSOT/Autosync
  if (S.ssot && S.ssot.ok) {
    if (S.ssot.drift > 0 || S.ssot.repoSha !== S.ssot.ssotSha) {
      recs.push(`{yellow-fg}Docs autosync:{/yellow-fg} out of date (drift:${S.ssot.drift})`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Press E to emit rules`);
      recs.push(`  {yellow-fg}→{/yellow-fg} make -s rules.emit`);
    }
  }
  
  // Proofs / Guards
  if (S.proofs && S.proofs.ok) {
    const p = S.proofs.latest?.json || {};
    if (p && (p.latency_ms === 0 || p.used === 0)) {
      recs.push(`{red-fg}QA guard failing{/red-fg}`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Press P to open latest proof`);
      recs.push(`  {yellow-fg}→{/yellow-fg} make -s guards.qa.latency`);
    }
  }
  
  if (!recs.length) {
    recs.push(`{green-fg}All green. No actions required.{/green-fg}`);
  }
  
  // Add notifications
  const notifs = loadNotifs().slice(-5).reverse();
  if (notifs.length > 0) {
    recs.push(`\n{cyan-fg}Recent Notifications:{/cyan-fg}`);
    notifs.forEach(n => {
      const color = n.kind === 'err' ? 'red' : n.kind === 'warn' ? 'yellow' : 'green';
      const time = new Date(n.ts).toLocaleTimeString();
      recs.push(`  {${color}-fg}${time}:{/${color}-fg} ${n.msg}`);
    });
  }
  
  return recs.join('\n');
}

// Hotkey action functions
async function actionEmitRules(){
  log("[ui] emit rules…");
  try {
    const r = await fetch("http://localhost:8700/api/actions/rules.emit", {method:"POST"});
    const j = await r.json();
    if (j.ok) {
      log("[ok] rules.emit");
      addNotif("ok", "Rules emitted successfully");
      const autosyncIdx = CONFIG.tiles.findIndex(t => t.type === "command");
      const rulesIdx = CONFIG.tiles.findIndex(t => t.type === "rules");
      if (autosyncIdx >= 0) await updateTile(CONFIG.tiles[autosyncIdx], boxes[autosyncIdx]);
      if (rulesIdx >= 0) await updateTile(CONFIG.tiles[rulesIdx], boxes[rulesIdx]);
      refreshGuidance();
      screen.render();
    } else {
      log(`[fail] rules.emit: ${j.error||"error"}`);
      addNotif("err", `rules.emit failed: ${j.error||"error"}`);
    }
  } catch (e) {
    log(`[fail] rules.emit: ${e.message}`);
    addNotif("err", `rules.emit failed: ${e.message}`);
  }
}

async function openLatestProof(){
  try {
    const r = await fetch("http://localhost:8700/api/proofs/latest-body");
    const j = await r.json();
    if (!j.ok) {
      log(`[fail] proof open: ${j.error}`);
      addNotif("err", `No proofs to open: ${j.error}`);
      return;
    }
    addNotif("ok", `Opened latest proof: ${j.file}`);
    // simple in-pane viewer; replace with a modal if you have one
    log(`[proof] ${j.file}\n${j.body.slice(0,1200)}${j.body.length>1200?"\n…":""}`);
  } catch (e) {
    log(`[fail] proof open: ${e.message}`);
    addNotif("err", `Proof open failed: ${e.message}`);
  }
}

function showLmChecklist(){
  log("LM Studio checklist:\n• Start chat model (e.g., qwen3-8b-instruct)\n• Start embed model (e.g., qwen3-embedding-0.6b)\n• Verify /v1/models");
}

function showGroqChecklist(){
  log("Groq checklist:\n• Get API key: https://console.groq.com/login\n• export GROQ_API_KEY=your_new_key_here\n• export GROQ_MODEL=llama-3.3-70b-versatile\n• curl /api/groq/model → ok:true\n• Current key appears invalid/expired (HTTP 401)");
}

// ---------- Helpers ----------
const exists = (p) => fs.existsSync(path.join(ROOT, p));
const stat = (p) => fs.statSync(path.join(ROOT, p));
const read = (p) => fs.readFileSync(path.join(ROOT, p), "utf8");
function run(cmd) {
  return new Promise((res) => {
    exec(cmd, { cwd: ROOT, env: process.env }, (err, stdout, stderr) => {
      res({ code: err ? (typeof err.code === "number" ? err.code : 1) : 0, stdout: (stdout||"").trim(), stderr: (stderr||"").trim() });
    });
  });
}

// API helpers
async function fetchJson(url) {
  try {
    const { statusCode, body } = await request(url, { method: "GET", maxRedirections: 1, headersTimeout: 5000 });
    if (statusCode >= 200 && statusCode < 300) {
      const text = await body.text();
      return JSON.parse(text);
    } else {
      return { ok: false, error: `HTTP ${statusCode}` };
    }
  } catch (e) {
    return { ok: false, error: String(e.message) };
  }
}

function ok(el, text, fresh = true) {
  el.textContent = text + (fresh ? " • ⬤" : " • ⚠");
  el.className = "tile ok";
}
function fail(el, lines, fresh = true) {
  el.className = "tile fail";
  el.innerHTML = lines.map(l => `<div class="errline">• ${escapeHtml(l)}</div>`).join("") + (fresh ? " • ⬤" : " • ⚠");
}
function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[m]));
}

function isFresh(ts, maxSec = 90) {
  if (!ts) return false;
  return (Date.now() - Date.parse(ts)) <= maxSec * 1000;
}

function withHeartbeat(text, fresh) {
  return `${text} ${fresh ? '• ⬤' : '• ⚠'}`;
}

async function healthz(url) {
  try {
    const { statusCode, body } = await request(url, { method: "GET", maxRedirections: 1, headersTimeout: 800 });
    if (statusCode >= 200 && statusCode < 300) {
      let txt = await body.text();
      return { ok: true, text: txt.slice(0, 160) };
    }
  } catch (_) {}
  return { ok: false };
}

function since(ts) {
  const d = Math.max(0, Date.now() - ts);
  if (d < 2000) return `${Math.round(d)}ms ago`;
  if (d < 60000) return `${Math.round(d/1000)}s ago`;
  return `${Math.round(d/60000)}m ago`;
}

async function gitSummary(paths) {
  const targets = paths && paths.length ? paths.map(p => `"${p}"`).join(" ") : ".";
  const st = await run(`git status --porcelain ${targets}`);
  const changed = st.stdout ? st.stdout.split("\n").filter(Boolean).length : 0;
  const last = await run(`git log -1 --pretty=format:'%cr • %h • %s' ${targets}`);
  const br = await run("git rev-parse --abbrev-ref HEAD");
  return { changed, last: last.stdout || "no commits", branch: br.stdout || "unknown" };
}

async function getSsotFileCount() {
  try {
    const r = await run("git -C docs/SSOT ls-files | wc -l");
    return r.stdout.trim() || "0";
  } catch {
    return "0";
  }
}

function excerptErrors(text, n = 3) {
  const lines = (text || "").split("\n").filter(Boolean);
  const errs = lines.filter(l => l.includes("::error ::") || /error/i.test(l));
  return errs.slice(0, n).map(s => s.replace(/^.*::error ::/, "• "));
}

function parseFirstFail(text) {
  // matches our guard format: "::error ::<type> in <path> — <msg>"
  const m = /::error ::.*? in (.+?) — (.+)/.exec(text || "");
  return m ? { path: m[1], msg: m[2] } : null;
}

function summarizeProofFile(absPath) {
  try {
    const raw = fs.readFileSync(absPath, "utf8");
    const j = JSON.parse(raw);
    const out = [];
    if ("latency_ms" in j || (j.meta && "latency_ms" in j.meta)) {
      const lat = j.latency_ms ?? j.meta?.latency_ms;
      const used = j.used ?? j.meta?.used;
      const analysis = (j.analysis ?? j.qa_analysis ?? j.data?.analysis ?? "").toString();
      out.push(`latency_ms=${lat}`, `used=${used}`, `analysis=${analysis ? analysis.slice(0,60) : "<empty>"}`);
    }
    // try scores
    const arr = j.items || j.candidates || j.results || j.data?.items || j.data?.candidates || j.data?.results;
    if (Array.isArray(arr) && arr.length) {
      const scores = arr.map(x => x && typeof x.score === "number" ? x.score : null).filter(v => v!=null);
      if (scores.length) out.push(`scores: ${scores.slice(0,5).map(s=>s.toFixed(3)).join(", ")}`);
    }
    return out.length ? out : ["(unable to summarize)"];
  } catch {
    return ["(failed to read proof)"];
  }
}

// ---------- Tile updaters ----------
async function updateTile(tileCfg, box) {
  const t = { status: "unknown", lines: [] };
  try {
    switch (tileCfg.type) {
      case "service": {
        // LM Studio - show actual models
        const j = await fetchJson("http://localhost:8700/api/lm/models?cb=" + Date.now());
        if (!j.ok) {
          t.status = "error";
          t.lines.push(withHeartbeat("unreachable ✖", isFresh(j.ts)));
          t.lines.push(`• ${j.error || "LM query failed"}`);
        } else {
          t.status = "ok";
          const chat = j.chat ? j.chat : "—";
          const embed = j.embed ? j.embed : "—";
          const msg = (j.reason && (chat === "—" || embed === "—"))
            ? `ping ✔ • ${j.reason}`
            : `ping ✔ • model:${chat} • embed:${embed}`;
          t.lines.push(withHeartbeat(msg, isFresh(j.ts)));
        }
        break;
      }
      case "env": {
        // Groq - show actual model
        const j = await fetchJson("http://localhost:8700/api/groq/model?cb=" + Date.now());
        if (j.missing?.length) {
          t.status = "error";
          t.lines.push(withHeartbeat("ping ✖ missing env:", isFresh(j.ts)));
          t.lines.push(`• ${j.missing.join(", ")}`);
        } else if (!j.ok) {
          t.status = "error";
          t.lines.push(withHeartbeat("ping ✖", isFresh(j.ts)));
          t.lines.push(`• ${j.error || `model ${j.model} not available`}`);
        } else {
          t.status = "ok";
          t.lines.push(withHeartbeat(`ping ✔ • model:${j.model}`, isFresh(j.ts)));
        }
        break;
      }
      case "git": {
        const s = await gitSummary(tileCfg.paths || ["."]);
        t.status = s.changed > 0 ? "busy" : "ok";
        t.lines.push(`branch: ${s.branch}`);
        t.lines.push(`changes: ${s.changed}`);
        t.lines.push(`last: ${s.last}`);
        break;
      }
      case "rules": {
        const j = await fetchJson("http://localhost:8700/api/ssot/status?cb=" + Date.now());
        if (!j.ok) {
          t.status = "error";
          t.lines.push(withHeartbeat("ssot status failed", isFresh(j.ts)));
          t.lines.push(`• ${j.error || "unknown error"}`);
        } else {
          const delta = j.rules - (lastRulesCount || 0);
          const deltaText = delta !== 0 ? ` (Δ${delta > 0 ? '+' : ''}${delta})` : '';
          t.status = j.rules > 0 ? "ok" : "warn";
          const staleWarn = j.stale ? " • stale" : "";
          t.lines.push(withHeartbeat(`rules:${j.rules}${deltaText} • last emit:${j.ssotSha} • ${j.ssotAge}${staleWarn}`, isFresh(j.ts)));
          if (j.rules === 0) t.lines.push("run: make rules.emit");
          lastRulesCount = j.rules;
        }
        break;
      }
      case "proofs": {
        const j = await fetchJson("http://localhost:8700/api/proofs/summary?cb=" + Date.now());
        if (!j.ok) {
          t.status = "error";
          t.lines.push(withHeartbeat("proofs summary failed", isFresh(j.ts)));
          t.lines.push(`• ${j.error || "unknown error"}`);
        } else if (j.count === 0) {
          t.status = "warn";
          t.lines.push(withHeartbeat("no proofs yet", isFresh(j.ts)));
        } else {
          t.status = "ok";
          const p = j.latest?.json || {};
          const ms = Number.isFinite(p.latency_ms) ? ` • ms:${p.latency_ms}` : "";
          const used = Number.isFinite(p.used) ? ` • used:${p.used}` : "";
          const why = p.reason || p.analysis ? ` • ${String(p.reason || p.analysis).slice(0, 60)}` : "";
          t.lines.push(withHeartbeat(`proofs:${j.count} • latest:${j.latest?.file || '—'} • ${j.latest?.age || '—'}${ms}${used}${why}`, isFresh(j.ts)));
        }
        break;
      }
      case "command": {
        const j = await fetchJson("http://localhost:8700/api/ssot/status?cb=" + Date.now());
        if (!j.ok) {
          t.status = "error";
          t.lines.push(withHeartbeat("ssot status failed", isFresh(j.ts)));
          t.lines.push(`• ${j.error || "unknown error"}`);
        } else {
          const drift = j.drift ? ` • drift:${j.drift}` : "";
          const status = j.repoSha === j.ssotSha && !j.drift ? "synced ✔" : "✖ out of date";
          t.status = status.includes("✔") ? "ok" : "error";
          t.lines.push(withHeartbeat(`${status} • SSOT:${j.ssotSha}/${j.ssotAge} • repo:${j.repoSha}/${j.repoAge}${drift}`, isFresh(j.ts)));
        }
        break;
      }
      case "commands_detailed": {
        let okAll = true, errorBlob = "";
        for (const c of tileCfg.cmds) {
          const r = await run(c);
          const name = c.replace(/^make\s+-s\s+/, "");
          const ok = r.code === 0;
          okAll = okAll && ok;
          if (!ok) {
            errorBlob += r.stderr + "\n";
          }
        }
        t.status = okAll ? "ok" : "error";
        if (okAll) {
          t.lines.push("✔ all guards");
        } else {
          // Show first failing proof filename and why
          const ff = parseFirstFail(errorBlob);
          if (ff) {
            t.lines.push(`✖ ${ff.path.split('/').pop()}`);
            t.lines.push(`• ${ff.msg}`);
            // Try to get proof details if file exists
            if (fs.existsSync(ff.path)) {
              const proofDetails = summarizeProofFile(ff.path);
              if (proofDetails.length > 0) {
                t.lines.push(`• ${proofDetails[0]}`);
              }
            }
          } else {
            t.lines.push("✖ guard failed");
            const errs = excerptErrors(errorBlob, 2);
            t.lines.push(...errs);
          }
        }
        break;
      }
    }
  } catch (e) {
    t.status = "error";
    t.lines.push(String(e.message || e).slice(0, 120));
  }
  setState(box, { status: t.status, lines: t.lines, blink: t.status === "busy" });
}

// ---------- Wire up tiles ----------
const boxes = CONFIG.tiles.map((tile, i) => addTile(i, tile.title));

// Track previous counts for delta calculation
let lastRulesCount = 0;

// File watching now handled by SSE - removed old chokidar watcher

// Initial render once
CONFIG.tiles.forEach(async (t, i) => {
  await updateTile(t, boxes[i]);
});
screen.render();

// Fast polling for all tiles (1 second intervals)
setInterval(async () => {
  await Promise.all(CONFIG.tiles.map(async (t, i) => {
    await updateTile(t, boxes[i]);
  }));
  refreshGuidance(); // Update guidance with each poll
  screen.render();
}, 1000);

// Keyboard controls
screen.key(["q", "C-c"], () => process.exit(0));

// Hotkeys
screen.key(["E"], actionEmitRules);
screen.key(["P"], openLatestProof);
screen.key(["L"], showLmChecklist);
screen.key(["G"], showGroqChecklist);
screen.key(["R"], refreshGuidance); // Refresh guidance

// Focus management
let currentTile = 0;
function updateFocus() {
  // Update visual focus indicator
  tiles.forEach((tile, idx) => {
    if (idx === currentTile) {
      tile.style.border.fg = "cyan";
    } else {
      tile.style.border.fg = "gray";
    }
  });
  tiles[currentTile].focus();
  screen.render();
}

screen.key(["left", "h"], () => {
  currentTile = Math.max(0, currentTile - 1);
  updateFocus();
});
screen.key(["right", "l"], () => {
  currentTile = Math.min(tiles.length - 1, currentTile + 1);
  updateFocus();
});

// Help overlay
const helpBox = blessed.box({
  top: 'center',
  left: 'center',
  width: '60%',
  height: '60%',
  border: 'line',
  style: {
    border: { fg: 'cyan' },
    bg: 'black'
  },
  content: `
StoryMaker Live Dashboard

Navigation:
  ← → (h/l)  - Move between tiles
  ↑ ↓ (j/k)  - Scroll within focused tile
  Page Up/Dn - Scroll 5 lines within tile
  Home/End   - Jump to top/bottom of tile
  ?           - Toggle this help
  q           - Quit

Actions:
  E           - Emit rules (run rules.emit)
  P           - Open latest proof
  L           - Show LM Studio checklist
  G           - Show Groq checklist
  R           - Refresh guidance panel

Focus:
  - Current tile has cyan border
  - Use ← → to move between tiles
  - Use ↑ ↓ to scroll within focused tile
  - All tiles are scrollable independently

Tiles:
  LM Studio   - Service health (ping ✔)
  Groq        - Environment check (ping ✔ env ✓)
  AgentPM     - Git status (SSOT docs)
  StoryMaker  - Git status (entire repo)
  SSOT Rules  - .mdc file count with delta
  Envelopes   - Proof statistics with details
  Docs Autosync - Canonicalization with SHA proof
  Rerank & QA - Guard execution results

Guidance Panel (Right):
  - Shows actionable recommendations
  - Color-coded status indicators
  - Recent notifications history
  - Auto-updates with system state

Press any key to close this help.
  `,
  hidden: true
});
screen.append(helpBox);

// Help toggle
screen.key(["?"], () => {
  helpBox.toggle();
  screen.render();
});

// Close help on any key
helpBox.key(["*"], () => {
  helpBox.hide();
  updateFocus();
});

// Initial focus
updateFocus();

log("Dashboard started (q to quit, ? for help, ← → to navigate tiles, ↑ ↓ to scroll within focused tile, E/P/L/G/R for actions).");
