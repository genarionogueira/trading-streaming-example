import type { CodegenConfig } from "@graphql-codegen/cli";

const schema =
  process.env.NEXT_PUBLIC_GRAPHQL_HTTP || "http://localhost:8080/graphql";

const config: CodegenConfig = {
  schema,
  documents: ["src/**/*.{ts,tsx}"],
  ignoreNoDocuments: false,
  generates: {
    "src/gql/": {
      preset: "client",
      plugins: [],
    },
  },
};

export default config;
