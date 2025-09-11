import React from "react";

export default function OnboardingHint() {
  const [dismissed, setDismissed] = React.useState(
    typeof window !== "undefined" && localStorage.getItem("sm_onboard_v1") === "1"
  );
  if (dismissed) return null;
  return (
    <div className="mb-3 rounded-xl border border-zinc-800 bg-zinc-900/50 p-3 text-sm text-zinc-300">
      <div className="font-medium mb-1">Quick start</div>
      <ol className="list-decimal list-inside space-y-1 text-zinc-400">
        <li><b>Generate Outline</b> (⌘/Ctrl+Enter)</li>
        <li><b>Run Checks</b> (⌘/Ctrl+K)</li>
      </ol>
      <button
        className="mt-2 text-xs rounded border border-zinc-700 px-2 py-1 hover:bg-zinc-800"
        onClick={()=>{ localStorage.setItem("sm_onboard_v1","1"); setDismissed(true); }}
      >
        Dismiss
      </button>
    </div>
  );
}






