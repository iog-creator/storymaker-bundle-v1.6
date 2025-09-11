import React from "react";
import "./styles.css";
import HealthRow from "./components/HealthRow";
import ProofsMeter from "./components/ProofsMeter";
import NarrativePanel from "./components/NarrativePanel";
import RetrievalPanel from "./components/RetrievalPanel";

export default function App() {
  return (
    <div className="mx-auto max-w-5xl p-6 space-y-6">
      <h1 className="text-2xl font-semibold">StoryMaker Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2 space-y-4">
          <HealthRow />
          <NarrativePanel />
          <RetrievalPanel />
        </div>
        <ProofsMeter />
      </div>
    </div>
  );
}
