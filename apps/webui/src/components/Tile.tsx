import React from "react";

export default function Tile(props: { title: string; children?: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-4 shadow">
      <div className="text-sm text-zinc-400 mb-2">{props.title}</div>
      {props.children}
    </div>
  );
}
