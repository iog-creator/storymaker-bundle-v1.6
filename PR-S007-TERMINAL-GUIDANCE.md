# PR-S007 Terminal Dashboard — Guidance & Notifications

## 🎯 **What's New**

Updated the terminal dashboard (`live_dashboard.js`) to include the same guidance and notification features as the web dashboard:

### **1. Guidance Panel** 
- **Right-side panel**: Shows actionable recommendations with color-coded status
- **Real-time updates**: Refreshes automatically with system state
- **Command suggestions**: Exact commands to run for each issue
- **Keyboard shortcuts**: Press R to refresh guidance manually

### **2. Persistent Notifications**
- **File-based storage**: Notifications saved to `.dashboard_notifications.json`
- **Recent history**: Shows last 5 notifications in guidance panel
- **Color-coded**: Red (error), Yellow (warning), Green (success)
- **Duplicate prevention**: No spam from repeated events

### **3. Enhanced Actions**
- **Smart notifications**: All actions now generate persistent notifications
- **Guidance updates**: Actions automatically refresh guidance panel
- **Better feedback**: Clear success/failure messages

## 🔧 **Technical Implementation**

### **Layout Changes**
```javascript
// Expanded grid to 4 columns to make room for guidance
const grid = new contrib.grid({ rows: 4, cols: 4, screen });

// Guidance panel takes up right column
const guidanceBox = grid.set(0, 3, 3, 1, blessed.box, {
  label: " Guidance & Next Actions ",
  border: "line",
  style: { border: { fg: "cyan" } },
  scrollable: true,
  // ... other properties
});
```

### **Persistent Notifications**
```javascript
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
```

### **Guidance Computation**
```javascript
async function refreshGuidance() {
  try {
    const [lm, groq, ssot, proofs] = await Promise.allSettled([
      fetchJson("http://localhost:8700/api/lm/models?cb=" + Date.now()),
      fetchJson("http://localhost:8700/api/groq/model?cb=" + Date.now()),
      fetchJson("http://localhost:8700/api/ssot/status?cb=" + Date.now()),
      fetchJson("http://localhost:8700/api/proofs/summary?cb=" + Date.now()),
    ]);
    
    const S = { lm: lm.value, groq: groq.value, ssot: ssot.value, proofs: proofs.value };
    const guidance = buildGuidance(S);
    guidanceBox.setContent(guidance);
    screen.render();
  } catch (e) {
    guidanceBox.setContent(`Error loading guidance:\n${e.message}`);
    screen.render();
  }
}
```

### **Color-Coded Guidance**
```javascript
function buildGuidance(S) {
  const recs = [];
  
  // LM Studio
  if (S.lm && S.lm.ok) {
    if (!S.lm.chat || !S.lm.embed) {
      recs.push(`{cyan-fg}LM Studio:{/cyan-fg} start ${!S.lm.chat ? 'a chat model' : 'an embed model'}`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Press L for checklist`);
      recs.push(`  {yellow-fg}→{/yellow-fg} Models: qwen3-8b-instruct + qwen3-embedding-0.6b`);
    }
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
```

## 🚀 **How to Use**

### **1. Start Terminal Dashboard**
```bash
# Start API server
node tools/server/api.js

# Start terminal dashboard
node tools/live_dashboard.js
```

### **2. New Features**

#### **Guidance Panel (Right Side)**
- **Auto-updates**: Refreshes every second with system state
- **Color-coded**: Red (errors), Yellow (warnings), Green (success)
- **Actionable**: Shows exact commands to run
- **Scrollable**: Use ↑ ↓ to scroll through guidance

#### **Persistent Notifications**
- **File storage**: Saved to `.dashboard_notifications.json`
- **Recent history**: Shows last 5 notifications in guidance
- **Duplicate prevention**: No spam from repeated events
- **Timestamps**: Each notification shows when it occurred

#### **Enhanced Actions**
- **E**: Emit rules (with notification)
- **P**: Open latest proof (with notification)
- **L**: LM Studio checklist
- **G**: Groq checklist
- **R**: Refresh guidance panel
- **?**: Show help (updated with guidance info)

### **3. Navigation**
- **← →**: Move between tiles (including guidance panel)
- **↑ ↓**: Scroll within focused tile/guidance
- **Page Up/Down**: Scroll 5 lines within focused area
- **Home/End**: Jump to top/bottom of focused area

## 🎨 **Visual Design**

### **Guidance Panel**
- **Position**: Right column of the 4-column grid
- **Colors**: Cyan border, color-coded content
- **Content**: Actionable recommendations with commands
- **Notifications**: Recent history at bottom

### **Color Coding**
- **Red**: Errors and critical issues
- **Yellow**: Warnings and recommendations
- **Green**: Success and healthy status
- **Cyan**: Headers and navigation

### **Layout**
- **3x3 grid**: Main tiles on the left
- **Guidance panel**: Right column spanning 3 rows
- **Events log**: Bottom row spanning 3 columns
- **Responsive**: Adapts to terminal size

## 🧪 **Testing**

### **Manual Test Scenarios**

1. **Test Guidance Updates**:
   - Start terminal dashboard
   - Guidance should show current system state
   - Press R to refresh manually

2. **Test Notifications**:
   - Press E to emit rules
   - Should see notification in guidance panel
   - Check `.dashboard_notifications.json` file

3. **Test Navigation**:
   - Use ← → to move to guidance panel
   - Use ↑ ↓ to scroll through guidance
   - Use Page Up/Down for faster scrolling

4. **Test Actions**:
   - All actions should generate notifications
   - Guidance should update after actions
   - Commands should be clearly displayed

## 📋 **Files Modified**

1. `tools/live_dashboard.js` - Enhanced with guidance panel and notifications

## 🎯 **Benefits**

### **For Terminal Users**
- **Same features**: Terminal dashboard now has web dashboard features
- **Persistent context**: Notifications survive restarts
- **Actionable guidance**: Clear commands for each issue
- **Better workflow**: All-in-one terminal experience

### **For Development**
- **Consistent experience**: Same features across web and terminal
- **File-based storage**: Notifications persist across sessions
- **Real-time updates**: Guidance updates with system state
- **Professional UI**: Color-coded, scrollable interface

## 🔄 **Integration**

The terminal dashboard now provides:
- **Guidance panel** with actionable recommendations
- **Persistent notifications** with file-based storage
- **Enhanced actions** with better feedback
- **Consistent experience** with web dashboard

Both web and terminal dashboards now have the same powerful guidance and notification features!
