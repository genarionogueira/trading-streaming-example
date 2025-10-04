"use client";

import { useSubscription } from "@apollo/client/react";
import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
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
  const MAX_VISIBLE = 10;
  const queueRef = React.useRef<UiNewsItem[]>([]);
  const drainingRef = React.useRef(false);
  const itemsRef = React.useRef<UiNewsItem[]>([]);
  React.useEffect(() => {
    itemsRef.current = items;
  }, [items]);

  const drainOnce = React.useCallback(() => {
    const next = queueRef.current.shift();
    if (next) {
      setItems((prev) => {
        const trimmedPrev = prev.slice(0, MAX_VISIBLE - 1);
        const nextList = [next, ...trimmedPrev];
        return nextList;
      });
      window.setTimeout(drainOnce, 280);
    } else {
      drainingRef.current = false;
    }
  }, []);

  const enqueue = React.useCallback(
    (incoming: UiNewsItem[]) => {
      const present = new Set<string>([
        ...itemsRef.current.map((i) => i.id),
        ...queueRef.current.map((i) => i.id),
      ]);
      for (const it of incoming) {
        if (!present.has(it.id)) {
          queueRef.current.push(it);
          present.add(it.id);
        }
      }
      if (!drainingRef.current && queueRef.current.length > 0) {
        drainingRef.current = true;
        drainOnce();
      }
    },
    [drainOnce]
  );

  useSubscription<NewsFeedSubscription, NewsFeedSubscriptionVariables>(
    NewsFeedDocument,
    {
      variables: {
        intervalSeconds: 0.65,
        batchSize: 10,
      },
      onData: ({ data }) => {
        const payload = data?.data?.newsFeed;
        if (!payload) return;
        const incoming = payload.map((n) => ({
          id: `${n.id}-${n.timestamp}`,
          title: n.title,
          summary: n.summary,
          source: n.source,
          timestamp: n.timestamp,
        }));
        enqueue(incoming);
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
      {items.length === 0 ? (
        <div className="text-neutral-500">Waiting for news...</div>
      ) : (
        <div className="relative h-56 overflow-hidden">
          <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-6 bg-gradient-to-b from-[#0b0f10] to-transparent" />
          <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-6 bg-gradient-to-t from-[#0b0f10] to-transparent" />
          <div className="space-y-3">
            <AnimatePresence initial={false}>
              {items.map((n) => (
                <motion.div
                  key={n.id}
                  initial={{ y: -16, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  exit={{ y: 16, opacity: 0 }}
                  transition={{
                    type: "tween",
                    duration: 0.28,
                    ease: "easeOut",
                  }}
                  className="flex items-start justify-between gap-3"
                >
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
                    <div className="mt-1 text-xs text-neutral-500">
                      {n.summary}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
}
