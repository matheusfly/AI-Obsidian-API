# MCP Tools Fix Guide

## Issues Fixed

### 1. Context7 MCP Server ✅
- **Problem**: Using incorrect package `@modelcontextprotocol/server-everything`
- **Solution**: Updated to use `@context7/mcp-server@latest`
- **Status**: Ready to use with existing API key

### 2. Byterover MCP Server ⚠️
- **Problem**: Using URL-based configuration instead of command-based
- **Solution**: Updated to use `@byterover/mcp-server@latest` with proper environment variables
- **Status**: Needs API key configuration

## Quick Fix Steps

### Step 1: Run the Fix Script
```powershell
.\fix-mcp-tools.ps1
```

### Step 2: Get Byterover API Key
1. Visit [https://byterover.dev](https://byterover.dev)
2. Sign up or login
3. Get your API key from the dashboard
4. Replace `your_byterover_api_key_here` in `mcp.json` with your actual API key

### Step 3: Restart Cursor
1. Close Cursor completely
2. Reopen Cursor
3. Check MCP tools status - both should show green dots

## Updated MCP Configuration

The following changes were made to your `mcp.json`:

### Context7 (Fixed)
```json
"context7": {
  "command": "npx",
  "args": [
    "-y",
    "@context7/mcp-server@latest"
  ],
  "env": {
    "CONTEXT7_API_KEY": "ctx7sk-33afd784-9366-4ea8-acfe-4a24b11c24cc",
    "CONTEXT7_URL": "https://mcp.context7.com/mcp"
  }
}
```

### Byterover (Needs API Key)
```json
"byterover-mcp": {
  "command": "npx",
  "args": [
    "-y",
    "@byterover/mcp-server@latest"
  ],
  "env": {
    "BYTEROVER_API_KEY": "your_byterover_api_key_here",
    "BYTEROVER_MACHINE_ID": "1f07a91e-5ce8-6950-b300-56b817457f07"
  }
}
```

## Verification

After completing the setup:

1. **Context7**: Should show green dot and "11 tools, 3 prompts enabled"
2. **Byterover**: Should show green dot and "15 tools enabled"
3. **Shadcn-UI**: Should continue showing green dot and "12 tools enabled"

## Troubleshooting

If you still see red dots:

1. **Restart Cursor completely** (not just reload window)
2. **Check API keys** are valid and properly formatted
3. **Run the fix script** to ensure packages are installed
4. **Check Cursor logs** for any error messages

## Support

- Context7: [https://context7.com](https://context7.com)
- Byterover: [https://byterover.dev](https://byterover.dev)
- MCP Documentation: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
