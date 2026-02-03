# MCP Server Configuration

This directory contains Model Context Protocol (MCP) server configurations for integrating Claude with external services.

## Available Servers

### fal-docs-mcp
Provides Claude with FAL.ai API documentation for generating accurate image/video prompts and understanding model parameters.

## Setup

### Configure Claude Code

Add to your Claude Code MCP configuration (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "fal": {
      "url": "https://docs.fal.ai/mcp"
    }
  }
}
```

Then restart Claude Code for the changes to take effect.

## Available Tools (after setup)

Once configured, Claude will have access to FAL.ai documentation including:

| Resource | Description |
|----------|-------------|
| Model documentation | Parameters, capabilities, and examples for each model |
| API reference | Correct endpoint URLs and request formats |
| Best practices | Prompt engineering tips for each model type |

## Usage

With the FAL docs MCP server active, Claude can:

1. Look up correct API parameters for models like `fal-ai/fast-sdxl`, `fal-ai/flux/dev`, etc.
2. Understand aspect ratio and resolution options
3. Generate properly formatted API calls
4. Access prompt engineering guidelines

## Example Queries

Once connected, you can ask Claude things like:

- "What parameters does fal-ai/flux/dev accept?"
- "How do I use image-to-image with FAL?"
- "What's the correct format for LoRA weights?"

Claude will consult the FAL documentation to provide accurate answers.
