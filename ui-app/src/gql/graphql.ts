/* eslint-disable */
import { TypedDocumentNode as DocumentNode } from '@graphql-typed-document-node/core';
export type Maybe<T> = T | null;
export type InputMaybe<T> = T | null | undefined;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

export type NewsItem = {
  __typename?: 'NewsItem';
  id: Scalars['Int']['output'];
  source: Scalars['String']['output'];
  summary: Scalars['String']['output'];
  timestamp: Scalars['String']['output'];
  title: Scalars['String']['output'];
};

export type Position = {
  __typename?: 'Position';
  id: Scalars['Int']['output'];
  price: Scalars['Float']['output'];
  quantity: Scalars['Int']['output'];
  symbol: Scalars['String']['output'];
};

export type Price = {
  __typename?: 'Price';
  changePercent: Scalars['Float']['output'];
  price: Scalars['Float']['output'];
  symbol: Scalars['String']['output'];
  timestamp: Scalars['String']['output'];
};

export type Query = {
  __typename?: 'Query';
  ping: Scalars['String']['output'];
  positions: Array<Position>;
};

export type Subscription = {
  __typename?: 'Subscription';
  newsFeed: Array<NewsItem>;
  prices: Array<Price>;
};


export type SubscriptionNewsFeedArgs = {
  batchSize?: Scalars['Int']['input'];
  intervalSeconds?: Scalars['Float']['input'];
};


export type SubscriptionPricesArgs = {
  intervalSeconds?: Scalars['Float']['input'];
  symbols?: InputMaybe<Array<Scalars['String']['input']>>;
};

export type NewsFeedSubscriptionVariables = Exact<{
  intervalSeconds?: InputMaybe<Scalars['Float']['input']>;
  batchSize?: InputMaybe<Scalars['Int']['input']>;
}>;


export type NewsFeedSubscription = { __typename?: 'Subscription', newsFeed: Array<{ __typename?: 'NewsItem', id: number, title: string, summary: string, source: string, timestamp: string }> };

export type PricesSubscriptionVariables = Exact<{
  symbols?: InputMaybe<Array<Scalars['String']['input']> | Scalars['String']['input']>;
  intervalSeconds?: InputMaybe<Scalars['Float']['input']>;
}>;


export type PricesSubscription = { __typename?: 'Subscription', prices: Array<{ __typename?: 'Price', symbol: string, price: number, changePercent: number, timestamp: string }> };


export const NewsFeedDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"subscription","name":{"kind":"Name","value":"NewsFeed"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"intervalSeconds"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"batchSize"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Int"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"newsFeed"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"intervalSeconds"},"value":{"kind":"Variable","name":{"kind":"Name","value":"intervalSeconds"}}},{"kind":"Argument","name":{"kind":"Name","value":"batchSize"},"value":{"kind":"Variable","name":{"kind":"Name","value":"batchSize"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"id"}},{"kind":"Field","name":{"kind":"Name","value":"title"}},{"kind":"Field","name":{"kind":"Name","value":"summary"}},{"kind":"Field","name":{"kind":"Name","value":"source"}},{"kind":"Field","name":{"kind":"Name","value":"timestamp"}}]}}]}}]} as unknown as DocumentNode<NewsFeedSubscription, NewsFeedSubscriptionVariables>;
export const PricesDocument = {"kind":"Document","definitions":[{"kind":"OperationDefinition","operation":"subscription","name":{"kind":"Name","value":"Prices"},"variableDefinitions":[{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"symbols"}},"type":{"kind":"ListType","type":{"kind":"NonNullType","type":{"kind":"NamedType","name":{"kind":"Name","value":"String"}}}}},{"kind":"VariableDefinition","variable":{"kind":"Variable","name":{"kind":"Name","value":"intervalSeconds"}},"type":{"kind":"NamedType","name":{"kind":"Name","value":"Float"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"prices"},"arguments":[{"kind":"Argument","name":{"kind":"Name","value":"symbols"},"value":{"kind":"Variable","name":{"kind":"Name","value":"symbols"}}},{"kind":"Argument","name":{"kind":"Name","value":"intervalSeconds"},"value":{"kind":"Variable","name":{"kind":"Name","value":"intervalSeconds"}}}],"selectionSet":{"kind":"SelectionSet","selections":[{"kind":"Field","name":{"kind":"Name","value":"symbol"}},{"kind":"Field","name":{"kind":"Name","value":"price"}},{"kind":"Field","name":{"kind":"Name","value":"changePercent"}},{"kind":"Field","name":{"kind":"Name","value":"timestamp"}}]}}]}}]} as unknown as DocumentNode<PricesSubscription, PricesSubscriptionVariables>;