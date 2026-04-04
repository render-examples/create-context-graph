---
sidebar_position: 2
title: Quick Start
slug: /quick-start
---

# Quick Start

Get a context graph app running in under 5 minutes.

## Prerequisites

- **Python 3.11+** and **Node.js 18+**
- **Neo4j** -- one of: [Neo4j Aura](https://console.neo4j.io) (free cloud), Docker, or `@johnymontana/neo4j-local`
- **Anthropic API key** -- for the AI agent ([get one here](https://console.anthropic.com))

## 1. Scaffold

```bash
uvx create-context-graph my-app \
  --domain healthcare \
  --framework pydanticai \
  --demo-data
```

This generates a complete project in `./my-app/` with a FastAPI backend, Next.js frontend, and sample healthcare data.

### With MCP Server for Claude Desktop

```bash
uvx create-context-graph my-app \
  --domain healthcare \
  --framework pydanticai \
  --demo-data \
  --with-mcp
```

This generates an MCP server configuration alongside the web app. After setup, copy `mcp/claude_desktop_config.json` into your Claude Desktop config to query the knowledge graph directly from Claude.

:::tip
Use `--demo` instead of `--demo-data` to also reset the database and ingest data in one step (requires Neo4j connection).
:::

## 2. Set Up Neo4j

**Option A: Neo4j Aura (easiest)**

1. Create a free instance at [console.neo4j.io](https://console.neo4j.io)
2. Download the `.env` credentials file
3. Pass it during scaffold: `--neo4j-aura-env path/to/Neo4j-credentials.env`

**Option B: Docker**

```bash
cd my-app && docker compose up -d neo4j
```

**Option C: neo4j-local**

```bash
npx @johnymontana/neo4j-local
```

## 3. Configure Environment

```bash
cd my-app
cp .env.example .env
# Edit .env with your Neo4j credentials and Anthropic API key
```

## 4. Seed Data

```bash
cd backend
uv venv && uv pip install -e .
make seed
```

## 5. Start the App

In two terminals:

```bash
# Terminal 1: Backend
cd backend && make dev

# Terminal 2: Frontend
cd frontend && npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and start chatting with your healthcare knowledge graph.

## What's Next?

- [Full tutorial](/docs/tutorials/first-context-graph-app) -- detailed walkthrough with all options
- [CLI reference](/docs/reference/cli-options) -- all available flags
- [Domain catalog](/docs/reference/domain-catalog) -- browse all 22 built-in domains
- [Switch frameworks](/docs/how-to/switch-frameworks) -- try different AI agent frameworks
