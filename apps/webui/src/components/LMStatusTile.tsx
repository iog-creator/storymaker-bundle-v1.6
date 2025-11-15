import React from "react";
import type { LMIndicatorWidgetProps } from "../utils/lmIndicatorAdapter";

interface LMStatusTileProps {
  indicator: LMIndicatorWidgetProps;
  onClick?: () => void;
}

const colorClasses: Record<LMIndicatorWidgetProps["color"], string> = {
  grey: "bg-gray-400",
  green: "bg-green-500",
  yellow: "bg-yellow-500",
  red: "bg-red-500",
};

export const LMStatusTile: React.FC<LMStatusTileProps> = ({ indicator, onClick }) => {
  const bg = colorClasses[indicator.color] ?? colorClasses.grey;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg px-3 py-2 text-sm text-white shadow ${bg}`}
      title={indicator.tooltip_lines.join("\n")}
    >
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wide">
          LM Status
        </span>
        <span className="font-semibold">
          {indicator.label}
        </span>
      </div>
    </button>
  );
};
