"use client";

import { useSubscription } from "@apollo/client/react";
import * as React from "react";
import {
  NewsFeedDocument,
  type NewsFeedSubscription,
  type NewsFeedSubscriptionVariables,
} from "../gql/graphql";

type UiNewsItem = {
  id: string;
  title: string;
  summary: string;
  source: string;
  timestamp: string;
};

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

export default function NewsFeed() {
  const [items, setItems] = React.useState<UiNewsItem[]>([]);

  useSubscription<NewsFeedSubscription, NewsFeedSubscriptionVariables>(
    NewsFeedDocument,
    {
      variables: {
        intervalSeconds: 0.75,
        batchSize: 3,
      },
      onData: ({ data }) => {
        const payload = data?.data?.newsFeed;
        if (!payload) return;
        setItems(
          payload.map((n) => ({
            id: String(n.id),
            title: n.title,
            summary: n.summary,
            source: n.source,
            timestamp: n.timestamp,
          }))
        );
      },
      onError: (err) => {
        console.error("News subscription error:", err);
      },
    }
  );

  return (
    <div className="rounded-sm border border-neutral-800 bg-[#0b0f10] p-3 text-sm">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-medium text-neutral-200">News</h3>
      </div>
      <div className="space-y-3">
        {items.map((n) => (
          <div key={n.id} className="flex items-start justify-between gap-3">
            <div className="min-w-12 text-neutral-400">
              {formatTime(n.timestamp)}
            </div>
            <div className="flex-1">
              <div className="text-neutral-300">
                <span className="mr-2 rounded-sm bg-neutral-800 px-1.5 py-0.5 text-xs text-neutral-300">
                  {n.source}
                </span>
                {n.title}
              </div>
              <div className="mt-1 text-xs text-neutral-500">{n.summary}</div>
            </div>
          </div>
        ))}
        {items.length === 0 && (
          <div className="text-neutral-500">Waiting for news...</div>
        )}
      </div>
    </div>
  );
}
