"use client";

import { ApolloClient, InMemoryCache, HttpLink, split } from "@apollo/client";
import { ApolloProvider } from "@apollo/client/react";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { createClient as createWsClient } from "graphql-ws";
import { getMainDefinition } from "@apollo/client/utilities";
import React from "react";
import type { DocumentNode } from "graphql";

type ApolloWrapperProps = {
  children: React.ReactNode;
};

function createApolloClient() {
  const httpUrl =
    process.env.NEXT_PUBLIC_GRAPHQL_HTTP ?? "http://localhost:8080/graphql";
  const wsUrl =
    process.env.NEXT_PUBLIC_GRAPHQL_WS || "ws://localhost:8080/graphql";

  const httpLink = new HttpLink({ uri: httpUrl });

  // Only initialize WS link in the browser environment
  const isBrowser = typeof window !== "undefined";

  const wsLink = isBrowser
    ? new GraphQLWsLink(
        createWsClient({
          url: wsUrl,
        })
      )
    : null;

  const link =
    isBrowser && wsLink
      ? split(
          ({ query }) => {
            const definition = getMainDefinition(query as DocumentNode);
            return (
              definition.kind === "OperationDefinition" &&
              definition.operation === "subscription"
            );
          },
          wsLink,
          httpLink
        )
      : httpLink;

  return new ApolloClient({
    link,
    cache: new InMemoryCache(),
    ssrMode: false,
  });
}

export default function ApolloWrapper({ children }: ApolloWrapperProps) {
  const [client] = React.useState(() => createApolloClient());
  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
