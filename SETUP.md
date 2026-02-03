# Codeywood Setup Guide

This guide walks through setting up the Codeywood framework with the hybrid Claude + n8n architecture.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for self-hosted n8n) OR n8n cloud account
- Claude Code CLI with MCP support
- FAL.ai API key

## Quick Start (15 minutes)

### 1. Clone and Install Python Dependencies

```bash
cd /path/to/codeywood
cd scripts/generate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Required for FAL.ai API access
export FAL_KEY="your-fal-api-key"

# Required for n8n workflows to find generation scripts
export CODEYWOOD_ROOT="/path/to/codeywood"
```

Then reload: `source ~/.zshrc`

### 3. Install and Start n8n

```bash
# Install globally
npm install -g n8n

# Start n8n (environment variables must be set first)
n8n start
```

Open http://localhost:5678 and complete initial setup (create account).

### 4. Import n8n Workflows

1. Open n8n → Workflows → Import from File
2. Import each file from `n8n/` directory:
   - `cw-generate-character-refs.json`
   - `cw-validate-gate.json`
   - (others as they're created)
3. Activate each workflow

### 5. Create n8n API Key

1. n8n → Settings → API
2. Create new API key
3. Copy the key (you'll need it next)

### 6. Configure Claude Code MCP

Create or edit `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "n8n": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-n8n"],
      "env": {
        "N8N_HOST": "http://localhost:5678",
        "N8N_API_KEY": "your-api-key-from-step-5"
      }
    }
  }
}
```

Restart Claude Code to load MCP configuration.

### 7. Verify Setup

In Claude Code:

```
You: List available n8n workflows

Claude: [Calls n8n_list_workflows]
Available workflows:
- cw-generate-character-refs
- cw-validate-gate
...
```

## Creating Your First Project

### 1. Scaffold Project Structure

```bash
cp -r templates/project-scaffold projects/my-project
cp templates/PROJECT_CONFIG.yaml projects/my-project/
cp templates/.state.example.json projects/my-project/.state.json
```

### 2. Edit PROJECT_CONFIG.yaml

```yaml
project:
  name: "My Project"
  slug: "my-project"
  modality: "animation"

# Leave style_dna empty for now - will be locked after exploration
style_dna:
  locked: false
```

### 3. Start Production

In Claude Code, from your project directory:

```
You: Let's start story development for this project

Claude: [Reads PROJECT_CONFIG.yaml]
[Begins story-intake skill]
```

## Directory Structure After Setup

```
codeywood/
├── SKILL.md                      # Master skill for Claude
├── ARCHITECTURE.md               # System design
├── SETUP.md                      # This file
│
├── mcp/                          # MCP configuration
│   ├── README.md
│   └── claude_mcp_config.example.json
│
├── n8n/                          # n8n workflow definitions
│   ├── README.md
│   ├── cw-generate-character-refs.json
│   └── cw-validate-gate.json
│
├── schemas/                      # JSON schemas
│   └── state.schema.json
│
├── scripts/generate/             # Python generation tools
├── skills/                       # Claude skill definitions
├── references/                   # Knowledge base
├── templates/                    # Project scaffolding
└── projects/                     # Your productions
```

## Troubleshooting

### "n8n workflow not found"
- Ensure workflow is imported AND activated in n8n
- Check workflow name matches exactly (case-sensitive)

### "FAL_KEY not set"
- Verify environment variable is exported
- For n8n, set it in n8n's environment variables settings

### "MCP connection failed"
- Restart Claude Code after editing MCP config
- Verify n8n is running on the configured port
- Check API key is correct

### "Permission denied" on file operations
- n8n needs filesystem access to your projects directory
- For Docker n8n, mount the projects volume

## Advanced Configuration

### Using n8n Cloud Instead of Self-Hosted

1. Create account at https://n8n.io
2. Import workflows to cloud instance
3. Update MCP config with cloud URL:

```json
{
  "mcpServers": {
    "n8n": {
      "env": {
        "N8N_HOST": "https://your-instance.app.n8n.cloud",
        "N8N_API_KEY": "your-cloud-api-key"
      }
    }
  }
}
```

### Adding Custom Workflows

1. Create workflow in n8n UI
2. Export as JSON to `n8n/` directory
3. Follow naming convention: `cw-{action}-{target}.json`
4. Document in `n8n/README.md`

### Extending Generation Scripts

The Python scripts in `scripts/generate/` can be extended:
- Add new `--flag` options in `fal_generate.py`
- Create corresponding n8n workflows that call them
- Document new capabilities in `SKILL.md`

## Support

- Issues: https://github.com/your-repo/codeywood/issues
- Documentation: `docs/` directory
- Knowledge base: `references/KNOWLEDGE_BASE.md`
