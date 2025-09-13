#!/usr/bin/env node
import express from "express";
import fs from "fs";
import path from "path";
import { exec as _exec } from "child_process";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import fetch from "node-fetch";
import chokidar from "chokidar";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../..");

// Load environment variables from multiple sources
dotenv.config();
dotenv.config({ path: path.join(ROOT, '.env.local') });

// Environment loaded
const exec = (cmd) => new Promise((res, rej) => _exec(cmd, { cwd: ROOT }, (e, stdout, stderr) => e ? rej(e) : res({stdout,stderr})));

const app = express();
app.use(express.json());

// CORS support for web dashboard
app.use((req, res, next) => {
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.set("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }
  next();
});

// Make responses no-cache so the TUI always sees freshest data
app.use((req, res, next) => {
  res.set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate");
  res.set("Pragma", "no-cache");
  res.set("Expires", "0");
  next();
});
const now = () => new Date().toISOString();

// --- SSE: clients + broadcast helper ---------------------------------------
const sseClients = new Set();
function sseBroadcast(evt) {
  const data = `event: changed\ndata: ${JSON.stringify(evt)}\n\n`;
  for (const res of sseClients) try { res.write(data); } catch {}
}
app.get("/api/events", (req, res) => {
  res.set({
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-store",
    "Connection": "keep-alive",
  });
  res.flushHeaders();
  res.write(`event: hello\ndata: {"ts":"${now()}"}\n\n`);
  sseClients.add(res);
  req.on("close", () => sseClients.delete(res));
});

// --- File watchers (SSOT / rules / proofs) ----------------------------------
const watchers = [
  chokidar.watch("docs/SSOT", {ignoreInitial:true}),
  chokidar.watch(".cursor/rules/*.mdc", {ignoreInitial:true}),
  chokidar.watch("docs/proofs/agentpm/*.json", {ignoreInitial:true}),
];
for (const w of watchers) {
  w.on("add",  f => sseBroadcast({topic:"file", action:"add",  file:f, ts:now()}));
  w.on("change",f=> sseBroadcast({topic:"file", action:"chg",  file:f, ts:now()}));
  w.on("unlink",f=> sseBroadcast({topic:"file", action:"del",  file:f, ts:now()}));
}

// LM Studio: list models (report chat + embed)
app.get("/api/lm/models", async (req,res) => {
  try {
    const base = process.env.LM_STUDIO_ENDPOINT || "http://127.0.0.1:1234/v1";
    const r = await fetch(base + "/models", { headers: { Accept: "application/json" } });
    if (!r.ok) return res.json({ ok:false, error:`HTTP ${r.status}`, ts: now() });
    const j = await r.json(), names = (j?.data || []).map(m => m.id);
    // Prefer obvious chat models; fallback to any non-embedding model
    const chat  = names.find(n => /qwen|llama|mistral|phi|deepseek|gemma|yi|mixtral/i.test(n))
                 || names.find(n => !/embed|embedding/i.test(n)) || null;
    const embed = names.find(n => /embed|embedding/i.test(n)) || null;
    const reason = (!chat && !embed) ? "no models loaded in LM Studio" : (!chat ? "no chat model loaded" : (!embed ? "no embed model loaded" : null));
    return res.json({ ok:true, chat, embed, all:names, reason, ts: now() });
  } catch(e){ return res.json({ ok:false, error:String(e.message), ts: now() }); }
});

// Groq: env + availability check
app.get("/api/groq/model", async (req,res) => {
  const model = process.env.GROQ_MODEL;
  const key   = process.env.GROQ_API_KEY;
  if (!key)   return res.json({ ok:false, missing:["GROQ_API_KEY"], ts: now() });
  if (!model) return res.json({ ok:false, missing:["GROQ_MODEL"], ts: now() });
  try {
    const r = await fetch("https://api.groq.com/openai/v1/models", {
      headers:{ Authorization:`Bearer ${key}` }
    });
    if (!r.ok) {
      const why = (r.status===401) ? "HTTP 401 (invalid/expired API key)" :
                 (r.status===403) ? "HTTP 403 (forbidden / org)" : `HTTP ${r.status}`;
      return res.json({ ok:false, model, error: why, ts: now() });
    }
    const j = await r.json();
    const available = (j?.data||[]).some(m => m.id === model);
    return res.json({ ok:available, model, available, ts: now() });
  } catch(e){ return res.json({ ok:false, model, error:String(e.message), ts: now() }); }
});

// SSOT status (rules, sha/age, repo comparison, drift)
async function lastSsotSha() { return (await exec("git -C docs/SSOT log -1 --pretty=%h")).stdout.trim(); }
async function lastSsotIso() { return (await exec("git -C docs/SSOT log -1 --pretty=%cI")).stdout.trim(); }
async function repoShaAffectingSsot() { return (await exec("git log -1 --pretty=%h -- docs/SSOT")).stdout.trim(); }
async function repoIsoAffectingSsot() { return (await exec("git log -1 --pretty=%cI -- docs/SSOT")).stdout.trim(); }
async function driftCount() { return Number((await exec("git diff --name-only HEAD -- docs/SSOT | wc -l")).stdout.trim()) || 0; }
function ageFromIso(iso){ const dt=new Date(iso); const h=Math.floor((Date.now()-dt.getTime())/36e5); return h>=24?`${Math.floor(h/24)}d ago`:`${h}h ago`; }
function prettyAge(tms){ const m=Math.floor((Date.now()-tms)/6e4); if(m<60)return `${m}m ago`; const h=Math.floor(m/60); return h<24?`${h}h ago`:`${Math.floor(h/24)}d ago`; }

// Count modified/added/renamed .mdc rules in working tree
async function rulesDelta() {
  try {
    const out = (await exec(`git status --porcelain .cursor/rules/*.mdc 2>/dev/null | wc -l`)).stdout.trim();
    return Number(out) || 0;
  } catch { return 0; }
}
app.get("/api/ssot/status", async (req,res) => {
  try {
    const ssotIso = await lastSsotIso();
    const repoIso = await repoIsoAffectingSsot();
    const ssotSha = await lastSsotSha();
    const ssotAge = ageFromIso(ssotIso);
    const repoSha = await repoShaAffectingSsot();
    const repoAge = ageFromIso(repoIso);
    const drift   = await driftCount();
    const rules   = Number((await exec("ls .cursor/rules/*.mdc 2>/dev/null | wc -l")).stdout.trim()) || 0;
    const delta   = await rulesDelta();
    const hoursSince = (iso) => Math.floor((Date.now() - new Date(iso).getTime())/36e5);
    const stale = hoursSince(ssotIso) >= 24 || hoursSince(repoIso) >= 24;
    return res.json({ ok:true, ssotSha, ssotAge, repoSha, repoAge, drift, rules, delta, stale, ts: now() });
  } catch(e){ return res.json({ ok:false, error:String(e.message) }); }
});

// Proofs summary (count + latest json peek)
app.get("/api/proofs/summary", async (req,res) => {
  try {
    const base = "docs/proofs/agentpm";
    const list = fs.existsSync(base)
      ? fs.readdirSync(base).filter(f =>
          f.endsWith(".json") &&
          !/^sample_/.test(f) &&          // ignore samples
          !/^test_/.test(f)   &&          // ignore tests
          !/^bad\.json$/.test(f)          // legacy synthetic
        )
      : [];
    const count = list.length;
    let latest = null;
    if (count) {
      const withT = list.map(f => ({ f, t: fs.statSync(path.join(base,f)).mtimeMs }))
                        .sort((a,b)=>b.t-a.t);
      const f = withT[0].f; let json=null;
      try { json = JSON.parse(fs.readFileSync(path.join(base,f),"utf8")); } catch {}
      latest = { file:f, age: prettyAge(withT[0].t), json };
    }
    return res.json({ ok:true, count, latest, ts: now() });
  } catch(e){ return res.json({ ok:false, error:String(e.message), ts: now() }); }
});

// Latest proof content (tail)
app.get("/api/proofs/latest-body", async (req,res) => {
  try {
    const base = "docs/proofs/agentpm";
    const list = fs.readdirSync(base).filter(f =>
      f.endsWith(".json") &&
      !/^sample_/.test(f) &&          // ignore samples
      !/^test_/.test(f)   &&          // ignore tests
      !/^bad\.json$/.test(f)          // legacy synthetic
    );
    if (!list.length) return res.json({ok:false, error:"no proofs"});
    const withT = list.map(f => ({ f, t: fs.statSync(path.join(base,f)).mtimeMs }))
                      .sort((a,b)=>b.t-a.t);
    const p = path.join(base, withT[0].f);
    const body = fs.readFileSync(p,"utf8");
    return res.json({ ok:true, file:withT[0].f, body, ts: now() });
  } catch(e){ return res.json({ ok:false, error:String(e.message), ts: now() }); }
});

// Run rules.emit (non-blocking-ish, returned output)
app.post("/api/actions/rules.emit", async (req,res) => {
  try {
    const out = await exec("make -s rules.emit");
    return res.json({ ok:true, stdout:out.stdout, ts: now() });
  } catch(e){
    return res.json({ ok:false, error:String(e.message), stdout:e.stdout, stderr:e.stderr, ts: now() });
  }
});

// Autosync convenience (alias to rules.emit for now)
app.post("/api/actions/autosync", async (req,res) => {
  try {
    const out = await exec("make -s rules.emit");
    return res.json({ ok:true, stdout:out.stdout, ts: now() });
  } catch(e){
    return res.json({ ok:false, error:String(e.message), stdout:e.stdout, stderr:e.stderr, ts: now() });
  }
});

const PORT = process.env.DASHBOARD_API_PORT || 8700;
app.listen(PORT, () => {
  console.log(`Dashboard API server running on port ${PORT}`);
});
