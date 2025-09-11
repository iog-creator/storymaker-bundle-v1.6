import React from "react";
import "./styles.css";

export default function App() {
  return (
    <div className="mx-auto max-w-5xl p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-zinc-100">StoryMaker Dashboard</h1>
      <div className="text-zinc-100">
        <p>This is a test to see if the UI is working.</p>
        <div className="bg-zinc-900 p-4 rounded-lg">
          <p className="text-green-400">If you can see this, the UI is working!</p>
        </div>
      </div>
    </div>
  );
}
