# PR-S007 — Persistent Guidance, Legend, and Playbooks

## 🎯 **What's New**

Three powerful enhancements that replace disappearing toasts with **persistent guidance**:

### **1. Persistent Guidance Panel** 
- **Right-side panel**: Always visible guidance with "What to do next"
- **State-driven actions**: Computes recommendations from live system state
- **One-click fixes**: Action buttons for common issues (Emit rules, Checklists, etc.)
- **Auto-refresh**: Updates when system state changes

### **2. Persistent Notifications**
- **localStorage backed**: Notifications survive page refresh/restart
- **Timestamped entries**: Each notification shows when it occurred
- **Color-coded**: Green (success), Yellow (warning), Red (error)
- **Clear button**: Reset notifications when needed

### **3. Built-in Legend & Help**
- **H keybinding**: Press H to open comprehensive legend modal
- **Always-visible keybar**: Bottom footer with quick key reference
- **Tile explanations**: What each tile means and when it's healthy
- **Action guide**: Complete keymap and usage instructions

## 🔧 **Technical Implementation**

### **HTML Structure**
```html
<!-- Persistent Guidance -->
<aside id="guidance" class="guidance">
  <div class="guidance-header">
    <span>Guidance & Next Actions</span>
    <button id="guidance-refresh" title="Refresh">↻</button>
  </div>
  <div id="guidance-body" class="guidance-body">
    <div class="guidance-empty">Waiting for status…</div>
  </div>

  <div class="guidance-sep"></div>

  <div class="guidance-header">
    <span>Notifications (Persisted)</span>
    <button id="notif-clear" title="Clear">✕</button>
  </div>
  <div id="notif-list" class="notif-list"></div>
</aside>

<!-- Legend / Help -->
<div id="legend-modal" class="modal">
  <div class="modal-card">
    <div class="modal-header">
      <div class="modal-title">Legend & Keymap</div>
      <button id="legend-close">×</button>
    </div>
    <pre class="modal-body">
Tiles:
 • LM Studio      → chat + embed models; green when both loaded
 • Groq (Creative)→ GROQ_MODEL available with valid key
 • SSOT Rules     → count, Δ since last emit, last emit sha/age
 • Docs Autosync  → SSOT vs repo; drift:n shows un-emitted SSOT changes
 • Proofs         → count, latest proof file, age, ms, used
 • Guards         → first failing guard & first failing proof summary

Keymap:
 • E  Emit rules (autosync SSOT)
 • P  Open latest proof (modal)
 • L  LM Studio checklist
 • G  Groq checklist
 • H  This legend
 • q  Quit
    </pre>
  </div>
</div>

<!-- Sticky footer keys (always visible) -->
<footer class="keybar">
  Keys: E=Emit  P=Proof  L=LM  G=Groq  H=Help  q=Quit
</footer>
```

### **CSS Styling**
```css
/* Guidance Panel */
.guidance {
  position: fixed; right: 12px; top: 12px; bottom: 48px;
  width: 320px; background:#0e0e0e; border:1px solid #2a2a2a; 
  border-radius:10px; display:flex; flex-direction:column; 
  gap:8px; padding:10px; z-index: 9000;
}

/* Keybar */
.keybar {
  position: fixed; left: 0; right: 0; bottom: 0; height: 36px;
  display:flex; align-items:center; padding:0 12px; gap:10px;
  background:#0c0c0c; border-top:1px solid #222; 
  color:#cfcfcf; font-size:12px; z-index: 9001;
}
```

### **JavaScript Features**

#### **Persistent Notifications**
```javascript
const NOTIF_KEY = "dashboard.persist.notifs.v1";
function loadNotifs(){ try { return JSON.parse(localStorage.getItem(NOTIF_KEY)||"[]"); } catch{ return []; } }
function saveNotifs(list){ localStorage.setItem(NOTIF_KEY, JSON.stringify(list.slice(-200))); }
function addNotif(kind, msg){
  const list = loadNotifs();
  list.push({ kind, msg, ts: new Date().toISOString() });
  saveNotifs(list); renderNotifs();
}
```

#### **Guidance Computation**
```javascript
async function refreshGuidance(){
  const [lm, groq, ssot, proofs] = await Promise.allSettled([
    fetch(`${API_BASE}/api/lm/models?cb=${Date.now()}`).then(r=>r.json()).catch(()=>null),
    fetch(`${API_BASE}/api/groq/model?cb=${Date.now()}`).then(r=>r.json()).catch(()=>null),
    fetch(`${API_BASE}/api/ssot/status?cb=${Date.now()}`).then(r=>r.json()).catch(()=>null),
    fetch(`${API_BASE}/api/proofs/summary?cb=${Date.now()}`).then(r=>r.json()).catch(()=>null),
  ]);
  const S = { lm: lm.value, groq: groq.value, ssot: ssot.value, proofs: proofs.value };
  guidanceBody.innerHTML = buildGuidance(S);
  bindGuidanceButtons();
}
```

#### **Action Button Binding**
```javascript
function bindGuidanceButtons(){
  guidanceBody.querySelectorAll("button[data-act='emit']").forEach(b=>b.onclick = actionEmitRules);
  guidanceBody.querySelectorAll("button[data-act='open-proof']").forEach(b=>b.onclick = openLatestProof);
  guidanceBody.querySelectorAll("button[data-act='lm-checklist']").forEach(b=>b.onclick = showLmChecklist);
  guidanceBody.querySelectorAll("button[data-act='groq-checklist']").forEach(b=>b.onclick = showGroqChecklist);
}
```

## 🚀 **How to Use**

### **1. Start the System**
```bash
# Terminal 1: Start API server
node tools/server/api.js

# Terminal 2: Start dashboard  
make ui.live
# OR manually:
cd tools && python3 -m http.server 8080
```

### **2. Open Dashboard**
Navigate to: `http://localhost:8080/web_dashboard.html`

### **3. New Features**

#### **Guidance Panel (Right Side)**
- **Always visible**: Shows current system state and recommended actions
- **Action buttons**: Click to fix issues directly from guidance
- **Auto-updates**: Refreshes when system state changes
- **Refresh button**: Manual refresh if needed

#### **Persistent Notifications (Bottom of Guidance)**
- **Survives refresh**: Notifications persist across page reloads
- **Timestamped**: Each notification shows when it occurred
- **Color-coded**: Visual indication of notification type
- **Clear button**: Reset all notifications

#### **Legend Modal (Press H)**
- **Comprehensive help**: Explains all tiles and their meanings
- **Keymap reference**: Complete list of keyboard shortcuts
- **Usage tips**: When tiles are healthy vs. when they need attention

#### **Always-Visible Keybar (Bottom)**
- **Quick reference**: Essential keys always visible
- **No memorization**: Never need to remember keybindings

### **4. Guidance Examples**

#### **When LM Studio is Missing Models**
```
LM Studio: start a chat model. [Checklist]
```

#### **When SSOT Has Drift**
```
Docs autosync: out of date (drift:6). [Emit rules]
```

#### **When QA Guards are Failing**
```
QA guard failing. [Open latest proof]
```

#### **When Everything is Healthy**
```
All green. No actions required.
```

## 🧪 **Testing**

Run the test script to verify features:
```bash
./tools/test_guidance_features.sh
```

### **Manual Test Scenarios**

1. **Create SSOT drift**:
   ```bash
   echo "test" >> docs/SSOT/DRIFT_LOG.md
   # → Guidance should show "Docs autosync: out of date (drift:1)"
   # → Notifications should show "SSOT drift: 1 file(s)"
   ```

2. **Fix drift**:
   ```bash
   make -s rules.emit
   # → Guidance should clear autosync recommendation
   # → Notifications should show "SSOT changed"
   ```

3. **Test persistence**:
   - Refresh the page
   - Notifications should still be there
   - Guidance should still show current state

4. **Test legend**:
   - Press H
   - Modal should open with complete help
   - Press × or Escape to close

## 🎨 **Visual Design**

### **Guidance Panel**
- **Position**: Fixed right side, 320px wide
- **Layout**: Two sections - Guidance & Notifications
- **Colors**: Dark theme with subtle borders
- **Buttons**: Action buttons for common fixes

### **Notifications**
- **Persistence**: Stored in localStorage
- **Limit**: Keeps last 200 notifications
- **Colors**: Green (success), Yellow (warning), Red (error)
- **Timestamps**: Human-readable date/time

### **Legend Modal**
- **Size**: Responsive modal with scrollable content
- **Content**: Monospace font for code/keymap
- **Navigation**: Click × or press Escape to close

### **Keybar**
- **Position**: Fixed bottom, full width
- **Content**: Essential keybindings always visible
- **Style**: Subtle background, readable text

## 🔄 **Integration**

This enhancement integrates seamlessly with existing features:
- **SSE events**: Still work, now update guidance automatically
- **Keyboard shortcuts**: All existing shortcuts still work
- **Tile updates**: Real-time updates continue as before
- **Click actions**: Interactive tiles still work
- **Toasts**: Still available for immediate feedback

## 📋 **Files Modified**

1. `tools/web_dashboard.html` - Enhanced with guidance panel, legend, keybar, and persistent notifications

## 🎯 **Benefits**

### **For New Users**
- **No learning curve**: Legend explains everything
- **Clear guidance**: Always know what to do next
- **Visual cues**: Color-coded status indicators

### **For Experienced Users**
- **Quick actions**: One-click fixes for common issues
- **Persistent context**: Notifications survive refreshes
- **Always-visible help**: Keybar provides quick reference

### **For System Monitoring**
- **State-driven guidance**: Recommendations based on actual system state
- **Historical context**: Persistent notifications show system history
- **Action-oriented**: Not just status, but what to do about it

## 🚀 **Next Steps**

This creates a **self-documenting dashboard** that:
- **Guides users** through system issues
- **Provides context** with persistent notifications
- **Offers quick fixes** with action buttons
- **Explains everything** with built-in help

The dashboard now provides **persistent guidance** instead of disappearing toasts, making it much more useful for both new and experienced users!
