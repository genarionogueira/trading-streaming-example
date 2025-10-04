"use client";

type Risk = {
  netExposure: number;
  varPercent: number;
  maxDrawdown: number;
};

const mockRisk: Risk = {
  netExposure: 15250.75,
  varPercent: 2.1,
  maxDrawdown: 6.8,
};

export default function RiskPanel() {
  return (
    <div className="rounded-sm border border-neutral-800 bg-[#0b0f10] p-3 text-sm">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-medium text-neutral-200">Risk</h3>
      </div>
      <div className="space-y-2 text-neutral-300">
        <div className="flex items-center justify-between">
          <span className="text-neutral-400">Net Exposure</span>
          <span>${mockRisk.netExposure.toLocaleString()}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-neutral-400">VaR</span>
          <span>{mockRisk.varPercent.toFixed(2)}%</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-neutral-400">Max Drawdown</span>
          <span>{mockRisk.maxDrawdown.toFixed(2)}%</span>
        </div>
      </div>
    </div>
  );
}
