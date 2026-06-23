# Power BI MCP Server - Setup Guide

## What is this?

A Model Context Protocol (MCP) server that connects to Power BI and provides tools to:
- ✅ Read local PBIX files (metadata)
- ✅ Connect to Power BI Service (live datasets)
- ✅ List workspaces and datasets
- ✅ Extract tables, columns, and measures
- ✅ View DAX expressions

## Setup Instructions

### Step 1: Create Azure Service Principal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure AD** → **App registrations** → **New registration**
3. Name it: `PowerBI-MCP-Server`
4. Click **Register**

### Step 2: Get Credentials

Copy these values from the app registration:
- **Application (client) ID** → `POWERBI_CLIENT_ID`
- **Directory (tenant) ID** → `POWERBI_TENANT_ID`

### Step 3: Create Client Secret

1. Go to **Certificates & secrets** → **New client secret**
2. Copy the secret value → `POWERBI_CLIENT_SECRET`

### Step 4: Grant Power BI Permissions

1. Go to **API permissions** → **Add a permission**
2. Select **Power BI Service**
3. Select **Delegated permissions**
4. Check: `Dataset.Read.All`, `Workspace.Read.All`
5. Click **Add permissions**
6. Click **Grant admin consent**

### Step 5: Enable Service Principal in Power BI

1. Go to Power BI Admin Portal: https://app.powerbi.com/admin-portal
2. Go to **Tenant settings** → **Developer settings**
3. Enable: **Allow service principals to use Power BI APIs**

### Step 6: Configure Environment Variables

Create a `.env` file in the project directory:

```
POWERBI_CLIENT_ID=your-client-id
POWERBI_CLIENT_SECRET=your-client-secret
POWERBI_TENANT_ID=your-tenant-id
```

Or set them in PowerShell:

```powershell
$env:POWERBI_CLIENT_ID = "your-client-id"
$env:POWERBI_CLIENT_SECRET = "your-client-secret"
$env:POWERBI_TENANT_ID = "your-tenant-id"
```

## Available Tools

### Local File Tools
- **pbix_summary** - Get info about local PBIX file
- **list_tables** - Get PBIX file metadata

### Power BI Service Tools (requires credentials)
- **get_powerbi_workspaces** - List all workspaces
- **get_workspace_datasets** - List datasets in a workspace
- **get_dataset_tables** - List tables and columns in a dataset
- **get_dataset_measures** - List measures and DAX expressions

## Usage Examples

### Example 1: List Workspaces
```bash
node test-client.js
# Calls: get_powerbi_workspaces
```

### Example 2: Get Dataset Tables
```javascript
const result = await client.callTool({
  name: "get_dataset_tables",
  arguments: {
    workspace_id: "123e4567-e89b-12d3-a456-426614174000",
    dataset_id: "987f6543-e21c-34b5-d678-543210987654"
  }
});
```

### Example 3: Get Measures
```javascript
const result = await client.callTool({
  name: "get_dataset_measures",
  arguments: {
    workspace_id: "workspace-id",
    dataset_id: "dataset-id"
  }
});
```

## Starting the Server

```bash
# Start MCP server
node server.js

# Or run test client
node test-client.js
```

## Troubleshooting

### "Power BI credentials not configured"
- Check environment variables are set correctly
- Use `echo $env:POWERBI_CLIENT_ID` to verify

### "401 Unauthorized"
- Verify client credentials are correct
- Check tenant ID is correct
- Ensure app has Power BI API permissions

### "Grant admin consent" button grayed out?
- You need admin privileges to grant consent
- Ask your Azure AD admin to grant permissions

## Security Notes

⚠️ **Never commit credentials to Git!**
- Use `.env` files (add to `.gitignore`)
- Use environment variables only
- Store secrets in Azure Key Vault for production

## References

- [Power BI REST APIs](https://learn.microsoft.com/en-us/rest/api/power-bi/)
- [Service Principal Authentication](https://learn.microsoft.com/en-us/power-bi/developer/embedded/service-principal-authentication)
- [Model Context Protocol](https://modelcontextprotocol.io/)
