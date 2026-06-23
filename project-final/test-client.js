import { spawn } from "child_process";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

const serverProcess = spawn("node", ["server.js"]);

const transport = new StdioClientTransport({
  stdio: [serverProcess.stdin, serverProcess.stdout, process.stderr],
});

const client = new Client(
  { name: "test-client", version: "1.0.0" },
  { capabilities: {} }
);

try {
  await client.connect(transport);
  console.log("✅ Connected to MCP server!");

  // List available tools
  const tools = await client.listTools();
  console.log("\n📋 Available Tools:");
  tools.tools.forEach((tool) => {
    console.log(`  - ${tool.name}: ${tool.description}`);
  });

  // Call pbix_summary tool
  console.log("\n🔄 Calling pbix_summary...");
  const result = await client.callTool({ name: "pbix_summary", arguments: {} });
  console.log("\n📊 Result:");
  result.content.forEach((block) => {
    if (block.type === "text") {
      console.log(block.text);
    }
  });

  // Call list_tables tool
  console.log("\n🔄 Calling list_tables...");
  const tablesResult = await client.callTool({
    name: "list_tables",
    arguments: {},
  });
  console.log("\n📋 Result:");
  tablesResult.content.forEach((block) => {
    if (block.type === "text") {
      console.log(block.text);
    }
  });

  await client.close();
  console.log("\n✅ Test completed successfully!");
  process.exit(0);
} catch (error) {
  console.error("❌ Error:", error.message);
  process.exit(1);
}
