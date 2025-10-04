import { defineConfig } from "@graphql-hive/gateway";

export const gatewayConfig = defineConfig({
  proxy: {
    endpoint: "http://localhost:4001/graphql",
  },
});
