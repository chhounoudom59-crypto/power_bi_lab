import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { Extract } from "unzipper";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Power BI API Configuration
const POWER_BI_API_URLS = {
  auth: "https://login.microsoftonline.com/common/oauth2/v2.0/token",
  api: "https://api.powerbi.com/v1.0/myorg",
};

// Helper: Get Power BI access token
async function getPowerBIToken(clientId, clientSecret, tenantId) {
  if (!clientId || !clientSecret || !tenantId) {
    throw new Error(
      "Power BI credentials not configured. Set POWERBI_CLIENT_ID, POWERBI_CLIENT_SECRET, POWERBI_TENANT_ID"
    );
  }

  const params = new URLSearchParams({
    client_id: clientId,
    scope: "https://analysis.windows.net/powerbi/api/.default",
    client_secret: clientSecret,
    grant_type: "client_credentials",
  });

  const response = await fetch(
    `https://login.microsoftonline.com/${tenantId}/oauth2/v2.0/token`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params,
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get Power BI token: ${error}`);
  }

  const data = await response.json();
  return data.access_token;
}

// Helper: Call Power BI API
async function callPowerBIAPI(endpoint, token) {
  const response = await fetch(`${POWER_BI_API_URLS.api}${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Power BI API error: ${response.status} - ${error}`);
  }

  return await response.json();
}

// Helper: Extract PBIX and get metadata
async function extractPBIXModel(pbixPath) {
  if (!pbixPath) {
    throw new Error("PBIX path is undefined");
  }
  if (!fs.existsSync(pbixPath)) {
    throw new Error(`PBIX file not found at: ${pbixPath}`);
  }
  return new Promise((resolve, reject) => {
    const tempPath = path.join(__dirname, ".pbix_temp");
    fs.createReadStream(pbixPath)
      .pipe(Extract({ path: tempPath }))
      .on("close", () => {
        try {
          // Try to read Metadata file
          const metadataPath = path.join(tempPath, "Metadata");
          let metadata = null;
          
          if (fs.existsSync(metadataPath)) {
            const metadataContent = fs.readFileSync(metadataPath, "utf8");
            metadata = JSON.parse(metadataContent);
          }
          
          // Also try to read DataModel for additional info
          const dataModelPath = path.join(tempPath, "DataModel");
          let dataModelInfo = null;
          if (fs.existsSync(dataModelPath)) {
            const stats = fs.statSync(dataModelPath);
            dataModelInfo = {
              size: stats.size,
              compressed: true,
              format: "XPress9 (binary)"
            };
          }
          
          resolve({
            metadata,
            dataModel: dataModelInfo,
            pbixPath: path.basename(pbixPath)
          });
        } catch (err) {
          reject(err);
        }
      })
      .on("error", reject);
  });
}

// Helper: Clean up temp directory
function cleanupTemp() {
  const tempDir = path.join(__dirname, ".pbix_temp");
  if (fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true });
  }
}

// Helper: Get PBIX path
function getPBIXPath() {
  const paths = [
    path.join(__dirname, "lab.pbix"),
    path.join(__dirname, "..", "lab.pbix"),
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) return p;
  }
  return path.join(__dirname, "lab.pbix");
}

const server = new Server(
  {
    name: "powerbi-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define tools
const toolsList = [
  {
    name: "pbix_summary",
    description: "Get overall summary of a local Power BI file (PBIX)",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "list_tables",
    description: "Get file info for a local Power BI file",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "get_powerbi_workspaces",
    description: "List all Power BI workspaces (requires API credentials)",
    inputSchema: { 
      type: "object", 
      properties: {} 
    },
  },
  {
    name: "get_workspace_datasets",
    description: "List datasets in a Power BI workspace",
    inputSchema: { 
      type: "object", 
      properties: {
        workspace_id: { type: "string", description: "Power BI workspace ID" },
      },
      required: ["workspace_id"],
    },
  },
  {
    name: "get_dataset_tables",
    description: "List all tables and columns in a Power BI dataset",
    inputSchema: { 
      type: "object", 
      properties: {
        workspace_id: { type: "string", description: "Power BI workspace ID" },
        dataset_id: { type: "string", description: "Power BI dataset ID" },
      },
      required: ["workspace_id", "dataset_id"],
    },
  },
  {
    name: "get_dataset_measures",
    description: "List all measures in a Power BI dataset",
    inputSchema: { 
      type: "object", 
      properties: {
        workspace_id: { type: "string", description: "Power BI workspace ID" },
        dataset_id: { type: "string", description: "Power BI dataset ID" },
      },
      required: ["workspace_id", "dataset_id"],
    },
  },
];

// Register tool handlers with Zod schemas
const toolsListSchema = z.object({
  method: z.literal("tools/list"),
});

const toolsCallSchema = z.object({
  method: z.literal("tools/call"),
  params: z.object({
    name: z.string(),
    arguments: z.record(z.unknown()).optional(),
  }),
});

server.setRequestHandler(toolsListSchema, async () => ({
  tools: toolsList,
}));

server.setRequestHandler(toolsCallSchema, async (request) => {
  const { name, arguments: args } = request.params;

    try {
      if (name === "pbix_summary") {
        const pbixPath = getPBIXPath();
        if (!fs.existsSync(pbixPath)) {
          return {
            content: [{ type: "text", text: "❌ lab.pbix not found at " + pbixPath }],
          };
        }

        const pbixData = await extractPBIXModel(pbixPath);
        cleanupTemp();

        const meta = pbixData.metadata || {};
        const dataModel = pbixData.dataModel || {};
        
        const summary = `📊 Power BI Model Summary for ${pbixData.pbixPath}
📌 Metadata Version: ${meta.Version || "unknown"}
📌 Created From: ${meta.CreatedFrom || "unknown"}
📌 Power BI Release: ${meta.CreatedFromRelease || "unknown"}
📌 Auto-created Relationships: ${meta.AutoCreatedRelationships?.length || 0}

📦 Data Model:
  - Compressed Format: ${dataModel.format || "unknown"}
  - Size: ${dataModel.size ? (dataModel.size / 1024).toFixed(2) + " KB" : "unknown"}

⚠️ Note: The detailed model (tables, measures, columns) is stored in compressed format.
To extract full model details, use Power BI APIs or load the file in Power BI Desktop.`;

        return {
          content: [{ type: "text", text: summary }],
        };
      }

      if (name === "list_tables") {
        const pbixPath = getPBIXPath();
        if (!fs.existsSync(pbixPath)) {
          return {
            content: [{ type: "text", text: "❌ lab.pbix not found" }],
          };
        }

        const pbixData = await extractPBIXModel(pbixPath);
        cleanupTemp();

        const meta = pbixData.metadata || {};
        
        const info = `📋 Power BI File Information:

📄 File: ${pbixData.pbixPath}
📌 Version: ${meta.Version || "unknown"}
📌 Created From: ${meta.CreatedFrom || "unknown"}
📌 Release: ${meta.CreatedFromRelease || "unknown"}

🔗 Auto-created Relationships: ${meta.AutoCreatedRelationships?.length || 0}

ℹ️ To view detailed table and measure information:
   1. Open the PBIX file in Power BI Desktop
   2. Use Power BI REST APIs
   3. Use Tabular Editor 3 or similar tools`;

        return {
          content: [{ type: "text", text: info }],
        };
      }

      // Power BI API Tools
      if (name === "get_powerbi_workspaces") {
        try {
          const clientId = process.env.POWERBI_CLIENT_ID;
          const clientSecret = process.env.POWERBI_CLIENT_SECRET;
          const tenantId = process.env.POWERBI_TENANT_ID;

          if (!clientId || !clientSecret || !tenantId) {
            return {
              content: [{
                type: "text",
                text: `⚠️ Power BI credentials not configured.\n\nSet these environment variables:\n- POWERBI_CLIENT_ID\n- POWERBI_CLIENT_SECRET\n- POWERBI_TENANT_ID\n\nSee: https://learn.microsoft.com/en-us/power-bi/developer/embedded/service-principal-authentication`
              }]
            };
          }

          const token = await getPowerBIToken(clientId, clientSecret, tenantId);
          const data = await callPowerBIAPI("/groups", token);

          const workspaceList = data.value
            .map((ws) => `- ${ws.name} (${ws.id})`)
            .join("\n");

          return {
            content: [{
              type: "text",
              text: `📚 Power BI Workspaces:\n\n${workspaceList || "No workspaces found"}`
            }]
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: `❌ API Error: ${error.message}` }]
          };
        }
      }

      if (name === "get_workspace_datasets") {
        try {
          const { workspace_id } = args || {};
          if (!workspace_id) {
            return {
              content: [{ type: "text", text: "❌ workspace_id is required" }]
            };
          }

          const clientId = process.env.POWERBI_CLIENT_ID;
          const clientSecret = process.env.POWERBI_CLIENT_SECRET;
          const tenantId = process.env.POWERBI_TENANT_ID;

          if (!clientId || !clientSecret || !tenantId) {
            return {
              content: [{ type: "text", text: "❌ Power BI credentials not configured" }]
            };
          }

          const token = await getPowerBIToken(clientId, clientSecret, tenantId);
          const data = await callPowerBIAPI(`/groups/${workspace_id}/datasets`, token);

          const datasetList = data.value
            .map((ds) => `- ${ds.name} (${ds.id})`)
            .join("\n");

          return {
            content: [{
              type: "text",
              text: `📊 Datasets in workspace ${workspace_id}:\n\n${datasetList || "No datasets found"}`
            }]
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: `❌ API Error: ${error.message}` }]
          };
        }
      }

      if (name === "get_dataset_tables") {
        try {
          const { workspace_id, dataset_id } = args || {};
          if (!workspace_id || !dataset_id) {
            return {
              content: [{ type: "text", text: "❌ workspace_id and dataset_id are required" }]
            };
          }

          const clientId = process.env.POWERBI_CLIENT_ID;
          const clientSecret = process.env.POWERBI_CLIENT_SECRET;
          const tenantId = process.env.POWERBI_TENANT_ID;

          if (!clientId || !clientSecret || !tenantId) {
            return {
              content: [{ type: "text", text: "❌ Power BI credentials not configured" }]
            };
          }

          const token = await getPowerBIToken(clientId, clientSecret, tenantId);
          const data = await callPowerBIAPI(
            `/groups/${workspace_id}/datasets/${dataset_id}/tables`,
            token
          );

          const tableList = data.value
            .map((table) => {
              const cols = table.columns?.map((c) => c.name).join(", ") || "no columns";
              return `- ${table.name}: [${cols}]`;
            })
            .join("\n");

          return {
            content: [{
              type: "text",
              text: `📋 Tables in dataset ${dataset_id}:\n\n${tableList || "No tables found"}`
            }]
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: `❌ API Error: ${error.message}` }]
          };
        }
      }

      if (name === "get_dataset_measures") {
        try {
          const { workspace_id, dataset_id } = args || {};
          if (!workspace_id || !dataset_id) {
            return {
              content: [{ type: "text", text: "❌ workspace_id and dataset_id are required" }]
            };
          }

          const clientId = process.env.POWERBI_CLIENT_ID;
          const clientSecret = process.env.POWERBI_CLIENT_SECRET;
          const tenantId = process.env.POWERBI_TENANT_ID;

          if (!clientId || !clientSecret || !tenantId) {
            return {
              content: [{ type: "text", text: "❌ Power BI credentials not configured" }]
            };
          }

          const token = await getPowerBIToken(clientId, clientSecret, tenantId);
          const data = await callPowerBIAPI(
            `/groups/${workspace_id}/datasets/${dataset_id}/tables`,
            token
          );

          const measures = [];
          data.value.forEach((table) => {
            table.measures?.forEach((measure) => {
              measures.push(`- [${table.name}][${measure.name}]: ${measure.expression?.substring(0, 50) || "N/A"}...`);
            });
          });

          return {
            content: [{
              type: "text",
              text: `📐 Measures in dataset ${dataset_id}:\n\n${measures.join("\n") || "No measures found"}`
            }]
          };
        } catch (error) {
          return {
            content: [{ type: "text", text: `❌ API Error: ${error.message}` }]
          };
        }
      }

      return {
        content: [{ type: "text", text: `Unknown tool: ${name}` }],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Error: ${error.message}` }],
      };
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Power BI MCP server started");
}

main().catch((err) => {
  console.error("Server error:", err);
  process.exit(1);
});

process.on("SIGTERM", () => {
  process.exit(0);
});
