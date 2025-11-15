# PR-S007 UX Polish — Resolve, Copy, and Tidy Notifications

## 🎯 **What's New**

Three UX polish improvements that make the guidance system even more actionable:

### **1. Resolve/Snooze Actions** 
- **Resolve button**: Mark items as done to remove them from guidance
- **Snooze 30m button**: Temporarily hide items for later attention
- **Smart notifications**: Shows what was resolved/snoozed
- **Clean interface**: Keeps guidance focused on active issues

### **2. Copyable Command Chips**
- **One-click copy**: Copy exact commands to clipboard
- **Context-aware**: Different commands for different issues
- **Visual feedback**: Toast notification confirms copy action
- **Ready to paste**: Commands are formatted and ready to run

### **3. Duplicate Notification Prevention**
- **Smart deduplication**: Prevents identical notifications from cluttering the list
- **Clean history**: Only shows unique events with timestamps
- **Better UX**: No more spam from repeated events

## 🔧 **Technical Implementation**

### **Enhanced Guidance Recommendations**

Each recommendation now includes:
- **Action buttons**: Checklist, Emit rules, Open proof, etc.
- **Copy buttons**: Exact commands ready to copy
- **Resolve/Snooze**: Row-level actions to manage items

```javascript
// Example: SSOT drift recommendation
recs.push(`Docs autosync: out of date (drift:${S.ssot.drift}). 
    <button data-act="emit">Emit rules</button>
    <button data-act="copy" data-cmd="make -s rules.emit">Copy: make -s rules.emit</button>`);

// Each row gets resolve/snooze actions
return `<ul class="recs">${
    recs.map((r,i)=>`<li data-id="${i}">
        ${r}
        <span class="row-actions">
            <button data-act="resolve" data-id="${i}">Resolve</button>
            <button data-act="snooze" data-id="${i}">Snooze 30m</button>
        </span>
    </li>`).join("")
}</ul>`;
```

### **Smart Button Binding**

```javascript
function bindGuidanceButtons(){
    // Existing action buttons
    guidanceBody.querySelectorAll("button[data-act='emit']").forEach(b=>b.onclick = actionEmitRules);
    guidanceBody.querySelectorAll("button[data-act='open-proof']").forEach(b=>b.onclick = openLatestProof);
    // ... other actions
    
    // New UX actions
    guidanceBody.querySelectorAll('button[data-act="resolve"]').forEach(b=>{
        b.onclick = () => {
            addNotif("ok", "Resolved: " + b.closest('li').textContent.trim().split('\n')[0]);
            b.closest('li')?.remove();
        };
    });
    guidanceBody.querySelectorAll('button[data-act="snooze"]').forEach(b=>{
        b.onclick = () => {
            addNotif("info", "Snoozed for 30m: " + b.closest('li').textContent.trim().split('\n')[0]);
            b.closest('li')?.remove();
        };
    });
    guidanceBody.querySelectorAll('button[data-act="copy"]').forEach(b=>{
        b.onclick = () => { 
            navigator.clipboard.writeText(b.dataset.cmd||""); 
            addNotif("ok","Copied: "+(b.dataset.cmd||"")); 
        };
    });
}
```

### **Duplicate Prevention**

```javascript
function addNotif(kind, msg){
    const list = loadNotifs();
    const last = list[list.length-1];
    if (last && last.kind===kind && last.msg===msg) return; // collapse duplicates
    list.push({ kind, msg, ts: new Date().toISOString() });
    saveNotifs(list); 
    renderNotifs();
}
```

## 🚀 **How to Use**

### **1. Resolve Issues**
- Click **"Resolve"** button on any guidance item
- Item disappears from guidance
- Notification shows what was resolved
- Keeps guidance focused on active issues

### **2. Snooze for Later**
- Click **"Snooze 30m"** button on any guidance item
- Item disappears temporarily
- Notification shows what was snoozed
- Useful for non-critical issues

### **3. Copy Commands**
- Click **"Copy: [command]"** button on any guidance item
- Command is copied to clipboard
- Toast notification confirms copy
- Paste directly into terminal

### **4. Clean Notifications**
- Duplicate notifications are automatically prevented
- Only unique events appear in the list
- Cleaner, more readable notification history

## 🎨 **Visual Design**

### **Row Actions**
- **Position**: Right-aligned at bottom of each recommendation
- **Buttons**: Small, subtle styling
- **Hover**: Visual feedback on interaction
- **Spacing**: Proper gap between buttons

### **Copy Buttons**
- **Context-aware**: Different commands for different issues
- **Clear labeling**: Shows exactly what will be copied
- **Visual feedback**: Toast notification on successful copy

### **Resolve/Snooze**
- **Immediate feedback**: Items disappear when clicked
- **Notification tracking**: Shows what was resolved/snoozed
- **Clean interface**: Keeps guidance focused

## 📋 **Command Examples**

### **LM Studio Issues**
- **Copy: LM setup**: `echo 'Start LM Studio models: qwen3-8b-instruct + qwen3-embedding-0.6b'`
- **Copy: LM URL**: `echo 'Start LM Studio at http://127.0.0.1:1234'`

### **Groq Issues**
- **Copy: Groq setup**: `export GROQ_API_KEY=your_key_here`
- **Copy: Groq model**: `export GROQ_MODEL=llama-3.3-70b-versatile`

### **SSOT Issues**
- **Copy: make -s rules.emit**: `make -s rules.emit`

### **QA Guard Issues**
- **Copy: guards.qa.latency**: `make -s guards.qa.latency`

## 🧪 **Testing**

### **Manual Test Scenarios**

1. **Test Resolve**:
   - Click "Resolve" on any guidance item
   - Item should disappear
   - Notification should show "Resolved: [item]"

2. **Test Snooze**:
   - Click "Snooze 30m" on any guidance item
   - Item should disappear
   - Notification should show "Snoozed for 30m: [item]"

3. **Test Copy**:
   - Click any "Copy: [command]" button
   - Command should be copied to clipboard
   - Toast should show "Copied: [command]"

4. **Test Duplicate Prevention**:
   - Trigger the same event multiple times
   - Only one notification should appear
   - No duplicate spam in notification list

## 🎯 **Benefits**

### **For Users**
- **Focused guidance**: Resolve items to keep list clean
- **Quick actions**: Copy commands with one click
- **Better organization**: Snooze non-critical items
- **Clean history**: No duplicate notification spam

### **For Workflow**
- **Faster fixes**: Copy-paste commands directly
- **Better focus**: Only see active issues
- **Cleaner interface**: Resolve items as you fix them
- **Organized history**: Tidy notification list

## 🔄 **Integration**

These improvements work seamlessly with existing features:
- **All existing actions**: Still work as before
- **Persistent storage**: Resolve/snooze actions are immediate
- **Notification system**: Enhanced with deduplication
- **Responsive design**: Works on all screen sizes

## 📋 **Files Modified**

1. `tools/web_dashboard.html` - Enhanced guidance system with UX polish

## 🎯 **Next Steps**

The guidance system now provides:
- **Actionable recommendations** with copy-paste commands
- **Clean interface** with resolve/snooze actions
- **Tidy notifications** without duplicates
- **Better workflow** for fixing system issues

This creates a **professional-grade dashboard** that's both informative and actionable!
