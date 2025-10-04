"use client";

import { DataGrid, type Column } from "react-data-grid";
import "react-data-grid/lib/styles.css";
import { gql } from "@apollo/client";
import { useSubscription } from "@apollo/client/react";
import * as React from "react";

type StockRow = {
  symbol: string;
  price: number;
  change: number;
};

const columns: Column<StockRow>[] = [
  { key: "symbol", name: "Symbol", width: 120 },
  { key: "price", name: "Price", width: 120 },
  {
    key: "change",
    name: "Change",
    width: 120,
    renderCell({ row }) {
      const isUp = row.change >= 0;
      const colorClass = isUp ? "text-emerald-400" : "text-red-400";
      const sign = isUp ? "+" : "";
      return (
        <span className={colorClass}>{`${sign}${row.change.toFixed(2)}%`}</span>
      );
    },
  },
  {
    key: "actions",
    name: "Actions",
    width: 160,
    frozen: true,
    renderCell({ row }) {
      function handleClick(type: "buy" | "sell", e: React.MouseEvent) {
        e.stopPropagation();
        // Placeholder: wire to backend later
        console.log(`${type.toUpperCase()} ${row.symbol}`);
      }
      return (
        <div className="flex gap-2">
          <button
            onClick={(e) => handleClick("buy", e)}
            className="rounded-sm bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-500"
          >
            Buy
          </button>
          <button
            onClick={(e) => handleClick("sell", e)}
            className="rounded-sm bg-red-600 px-2 py-1 text-xs text-white hover:bg-red-500"
          >
            Sell
          </button>
        </div>
      );
    },
  },
];

const DEFAULT_SYMBOLS: string[] = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"];

const PRICES_SUBSCRIPTION = gql`
  subscription Prices($symbols: [String!], $intervalSeconds: Float) {
    prices(symbols: $symbols, intervalSeconds: $intervalSeconds) {
      symbol
      price
      changePercent
      timestamp
    }
  }
`;

type PricesData = {
  prices: Array<{
    symbol: string;
    price: number;
    changePercent: number;
    timestamp: string;
  }>;
};

type PricesVars = {
  symbols?: string[];
  intervalSeconds?: number;
};

export default function StockGrid() {
  const [rows, setRows] = React.useState<StockRow[]>([]);

  const { data, error } = useSubscription<PricesData, PricesVars>(
    PRICES_SUBSCRIPTION,
    {
      variables: {
        symbols: DEFAULT_SYMBOLS,
        intervalSeconds: 1.0,
      },
      onData: ({ data }) => {
        const payload = data?.data;
        if (!payload?.prices) return;
        setRows(
          payload.prices.map((p) => ({
            symbol: p.symbol,
            price: p.price,
            change: p.changePercent,
          }))
        );
      },
      onError: (err) => {
        // Helpful when testing locally
        console.error("Subscription error:", err);
      },
    }
  );

  React.useEffect(() => {
    if (data?.prices) {
      setRows(
        data.prices.map((p) => ({
          symbol: p.symbol,
          price: p.price,
          change: p.changePercent,
        }))
      );
    }
  }, [data]);

  return (
    <div className="h-[320px] w-full overflow-hidden rounded-sm">
      {error ? (
        <div className="p-2 text-sm text-red-400">
          Failed to subscribe to prices
        </div>
      ) : (
        <DataGrid
          columns={columns}
          rows={rows}
          rowKeyGetter={(row) => row.symbol}
          className="rdg-dark text-sm"
        />
      )}
    </div>
  );
}
