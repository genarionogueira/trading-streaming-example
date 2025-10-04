"use client";

type Position = {
  symbol: string;
  quantity: number;
  avgPrice: number;
};

const mockPositions: Position[] = [
  { symbol: "AAPL", quantity: 50, avgPrice: 210.12 },
  { symbol: "MSFT", quantity: 20, avgPrice: 380.5 },
];

export default function PositionsPanel() {
  return (
    <div className="rounded-sm border border-neutral-800 bg-[#0b0f10] p-3 text-sm">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-medium text-neutral-200">Positions</h3>
      </div>
      <div className="space-y-2">
        {mockPositions.map((p) => (
          <div
            key={p.symbol}
            className="flex items-center justify-between text-neutral-300"
          >
            <span className="w-16 text-neutral-400">{p.symbol}</span>
            <span className="w-20 text-right">{p.quantity}</span>
            <span className="w-24 text-right">${p.avgPrice.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
