# PR-S006 — Interactive Dashboard Enhancements

## 🎯 **What's New**

Three powerful enhancements to the StoryMaker live dashboard:

### **1. Interactive Tiles** 
- **Click to act**: Tiles now respond to clicks with meaningful actions
- **Rules tile**: Click to view detailed status or emit rules
- **Proofs tile**: Click to open latest proof in JSON modal
- **Autosync tile**: Click to run autosync action

### **2. Drill-Down Modals**
- **JSON viewer**: Latest proofs open in scrollable, prettified modal
- **Rules details**: Comprehensive status with tips and action hints
- **Modal controls**: Click × or press Escape to close

### **3. Smart Notifications**
- **Non-blocking toasts**: Appear in bottom-right corner
- **Drift alerts**: "SSOT drift: N file(s)" when files are out of sync
- **Out-of-date warnings**: "Docs out of date" when SSOT ≠ repo
- **QA failures**: "QA guard failing" when proofs show issues
- **Action feedback**: Success/fail toasts for all actions

## 🔧 **Technical Implementation**

### **Server Changes** (`tools/server/api.js`)
```javascript
// New autosync endpoint (alias to rules.emit)
app.post("/api/actions/autosync", async (req,res) => {
  try {
    const out = await exec("make -s rules.emit");
    return res.json({ ok:true, stdout:out.stdout, ts: now() });
  } catch(e){
    return res.json({ ok:false, error:String(e.message), stdout:e.stdout, stderr:e.stderr, ts: now() });
  }
});
```

### **UI Enhancements** (`tools/web_dashboard.html`)

#### **HTML Structure**
```html
<!-- Toasts -->
<div id="toasts" class="toasts"></div>

<!-- Modal -->
<div id="modal" class="modal">
  <div class="modal-card">
    <div class="modal-header">
      <div class="modal-title">Details</div>
      <button id="modal-close">×</button>
    </div>
    <pre id="modal-body" class="modal-body"></pre>
  </div>
</div>
```

#### **CSS Styling**
- **Toasts**: Fixed positioning, smooth animations, color-coded borders
- **Modal**: Centered overlay, scrollable content, dark theme
- **Responsive**: Works on different screen sizes

#### **JavaScript Features**
```javascript
// Toast system
function toast(msg, kind="info", ttl=3500) { /* ... */ }

// Modal system  
function showModal(text, title="Details") { /* ... */ }
function showJsonModal(obj, title="Proof") { /* ... */ }

// Click handlers
document.getElementById("tile-rules").addEventListener("click", async () => {
  const r = await fetch(`${API_BASE}/api/ssot/status?cb=${Date.now()}`); 
  const j = await r.json();
  if (j?.ok) showRulesDetails(j); else actionEmitRules();
});

// Smart notifications
async function smartNotify(){
  const a = await (await fetch(`${API_BASE}/api/ssot/status?cb=${Date.now()}`)).json();
  if (a?.ok) {
    if (a.drift > 0) toast(`SSOT drift: ${a.drift} file(s)`, "warn", 2800);
    if (a.repoSha !== a.ssotSha) toast("Docs out of date", "warn", 2800);
  }
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

### **3. Interactive Features**

#### **Click Actions**
- **SSOT Rules tile** → Opens detailed status modal with tips
- **Envelopes & Proofs tile** → Opens latest proof JSON in modal
- **Docs Autosync tile** → Runs autosync action with feedback

#### **Keyboard Shortcuts** (unchanged)
- `E` - Emit rules
- `P` - Open latest proof  
- `L` - LM Studio checklist
- `G` - Groq checklist
- `Q` - Quit

#### **Smart Notifications**
- **Drift detected**: Yellow toast when SSOT files are out of sync
- **Docs out of date**: Warning when SSOT ≠ repo SHA
- **QA guard failing**: Red alert when proofs show issues
- **Action feedback**: Success/fail toasts for all operations

## 🧪 **Testing**

Run the test script to verify endpoints:
```bash
./tools/test_dashboard_features.sh
```

Expected output:
```
🧪 Testing StoryMaker Interactive Dashboard Features
==================================================
1. Checking API server...
   ✅ API server is running on port 8700
2. Testing autosync endpoint...
   ✅ Autosync endpoint working
3. Testing rules.emit endpoint...
   ✅ Rules.emit endpoint working
4. Testing proofs endpoint...
   ✅ Proofs endpoint working
5. Testing SSOT status endpoint...
   ✅ SSOT status endpoint working
```

## 🎨 **Visual Design**

### **Toast Notifications**
- **Position**: Bottom-right corner
- **Colors**: Green (success), Yellow (warning), Red (error)
- **Animation**: Smooth slide-in/fade-out
- **Duration**: 3.5s default, configurable per toast

### **Modal Windows**
- **Size**: Responsive (max 900px wide, 82vh tall)
- **Theme**: Dark background with light text
- **Content**: Monospace font for JSON/code
- **Controls**: Click × or press Escape to close

### **Interactive Tiles**
- **Hover**: Visual feedback on clickable tiles
- **Actions**: Immediate response to clicks
- **Feedback**: Toast notifications for all actions

## 🔄 **Integration**

This enhancement integrates seamlessly with existing features:
- **SSE events**: Still work, now with toast notifications
- **Keyboard shortcuts**: Unchanged functionality
- **Tile updates**: Real-time updates continue as before
- **API endpoints**: New autosync endpoint added

## 📋 **Files Modified**

1. `tools/server/api.js` - Added autosync endpoint
2. `tools/web_dashboard.html` - Enhanced with modals, toasts, click handlers
3. `tools/test_dashboard_features.sh` - New test script

## 🎯 **Next Steps**

The dashboard now provides:
- **Better UX**: Click-to-act instead of keyboard-only
- **More visibility**: Smart notifications for important changes  
- **Deeper insights**: Modal drill-downs for detailed information
- **Action feedback**: Clear success/failure indicators

This creates a more interactive and informative monitoring experience while maintaining all existing functionality.
