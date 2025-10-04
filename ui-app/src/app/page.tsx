"use client";

import dynamic from "next/dynamic";

const StockGrid = dynamic(() => import("../components/StockGrid"), {
  ssr: false,
});
const PositionsPanel = dynamic(() => import("../components/PositionsPanel"), {
  ssr: false,
});
const RiskPanel = dynamic(() => import("../components/RiskPanel"), {
  ssr: false,
});
const NewsFeed = dynamic(() => import("../components/NewsFeed"), {
  ssr: false,
});

export default function Home() {
  return (
    <main className="min-h-dvh p-6">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded-sm border border-neutral-800 bg-[#0b0f10] p-3">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-medium text-neutral-200">Market</h2>
          </div>
          <div className="p-1">
            <StockGrid />
          </div>
        </div>
        <NewsFeed />
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <PositionsPanel />
          <RiskPanel />
        </div>
      </div>
    </main>
  );
}
