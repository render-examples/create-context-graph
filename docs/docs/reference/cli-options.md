---
sidebar_position: 1
title: CLI Options & Flags
---

# CLI Options & Flags

Complete reference for the `create-context-graph` command-line interface.

## Command Signature

```
create-context-graph [PROJECT_NAME] [OPTIONS]
```

`PROJECT_NAME` is optional. If omitted but `--domain` and `--framework` are provided, a slug is auto-generated (e.g., `healthcare-pydanticai-app`). If neither project name nor required flags are provided, the interactive wizard launches.

## Options

| Option | Type | Env Variable | Default | Description |
|--------|------|-------------|---------|-------------|
| `--domain` | `string` | -- | *(wizard prompt)* | Domain ID (e.g., `financial-services`, `healthcare`, `software-engineering`). Use `--list-domains` to see all available IDs. |
| `--framework` | `choice` | -- | *(wizard prompt)* | Agent framework to use. One of: `pydanticai`, `claude-agent-sdk`, `strands`, `google-adk`, `openai-agents`, `langgraph`, `crewai`, `anthropic-tools`. |
| `--demo-data` | `flag` | -- | `false` | Generate synthetic demo data and write it to `data/fixtures.json` in the output project. Uses static placeholder data by default; pass `--anthropic-api-key` for LLM-generated realistic data. |
| `--custom-domain` | `string` | -- | -- | Natural language description of a custom domain (e.g., `"veterinary clinic management"`). Requires `--anthropic-api-key`. Generates a full ontology YAML from the description. |
| `--connector` | `string` (repeatable) | -- | -- | SaaS connector to enable. Can be specified multiple times. Supported values: `github`, `slack`, `jira`, `notion`, `gmail`, `gcal`, `salesforce`, `linear`, `google-workspace`, `claude-code`, `claude-ai`, `chatgpt`. |
| `--import-type` | `choice` | -- | -- | Chat history import type: `claude-ai` or `chatgpt`. Must be used with `--import-file`. |
| `--import-file` | `path` | -- | -- | Path to chat export file (`.zip`, `.json`, or `.jsonl`). Must be used with `--import-type`. |
| `--import-depth` | `choice` | -- | `fast` | Import extraction depth: `fast` (messages only) or `deep` (messages + tool call traces). |
| `--import-filter-after` | `string` | -- | -- | Only import conversations created after this date (ISO 8601). |
| `--import-filter-before` | `string` | -- | -- | Only import conversations created before this date (ISO 8601). |
| `--import-filter-title` | `string` | -- | -- | Only import conversations matching this title pattern (regex). |
| `--import-max-conversations` | `int` | -- | `0` (all) | Maximum conversations to import. `0` means no limit. |
| `--linear-api-key` | `string` | `LINEAR_API_KEY` | -- | Linear personal API key. Required when using `--connector linear`. |
| `--linear-team` | `string` | `LINEAR_TEAM` | -- | Linear team URL key (e.g., `ENG`). Filters the import to a single team. If omitted, all teams are imported. |
| `--gws-folder-id` | `string` | `GWS_FOLDER_ID` | -- | Google Drive folder ID to scope the import. Recommended to keep the graph focused. |
| `--gws-include-comments` / `--gws-no-comments` | `flag` | -- | on | Import comment threads from Docs/Sheets/Slides. Resolved threads become decision traces. |
| `--gws-include-revisions` / `--gws-no-revisions` | `flag` | -- | on | Import revision history metadata for each file. |
| `--gws-include-activity` / `--gws-no-activity` | `flag` | -- | on | Import Drive Activity events (create, edit, move, share, etc.). |
| `--gws-include-calendar` | `flag` | -- | off | Import Calendar events within the time range. Requires Google Calendar API enabled. |
| `--gws-include-gmail` | `flag` | -- | off | Import Gmail thread metadata (subject, participants -- no body text). Requires Gmail API enabled. |
| `--gws-since` | `string` | -- | 90 days ago | ISO date; only import activity after this date. |
| `--gws-mime-types` | `string` | -- | `docs,sheets,slides` | Comma-separated MIME type filter (`docs`, `sheets`, `slides`, `pdf`, `all`). |
| `--gws-max-files` | `int` | -- | `500` | Maximum number of files to import (safety limit). |
| `--claude-code-scope` | `choice` | -- | `current` | Import sessions from the `current` project (matching cwd) or `all` projects in `~/.claude/projects/`. |
| `--claude-code-project` | `string` | -- | -- | Explicit project path to import Claude Code sessions for. Overrides `--claude-code-scope`. |
| `--claude-code-since` | `string` | -- | all time | ISO date; only import sessions modified after this date. |
| `--claude-code-max-sessions` | `int` | -- | `0` (all) | Maximum number of sessions to import (most recent first). `0` means no limit. |
| `--claude-code-content` | `choice` | -- | `truncated` | Content storage mode: `full` (complete text), `truncated` (first 2000 chars), `none` (metadata only). |
| `--with-mcp` | `flag` | -- | `false` | Generate MCP server configuration for Claude Desktop. Creates `mcp/claude_desktop_config.json`, `mcp/README.md`, and adds a `make mcp-server` target to the Makefile. |
| `--mcp-profile` | `choice` | -- | `extended` | MCP tool profile: `core` (6 tools — basic memory operations) or `extended` (16 tools — full memory access including graph queries and reasoning traces). |
| `--session-strategy` | `choice` | -- | `per_conversation` | Memory session strategy: `per_conversation` (new session ID per conversation), `per_day` (sessions reset daily), `persistent` (single continuous session per user). |
| `--auto-extract` / `--no-auto-extract` | `flag` | -- | on | Automatically extract entities from conversation messages via neo4j-agent-memory's entity extraction pipeline. |
| `--auto-preferences` / `--no-auto-preferences` | `flag` | -- | on | Automatically detect user preferences from conversation messages. Detected preferences are stored in the knowledge graph. |
| `--ingest` | `flag` | -- | `false` | Ingest generated data into Neo4j after scaffolding. Requires a running Neo4j instance. |
| `--neo4j-uri` | `string` | `NEO4J_URI` | `neo4j://localhost:7687` | Neo4j Bolt connection URI. |
| `--neo4j-username` | `string` | `NEO4J_USERNAME` | `neo4j` | Neo4j authentication username. |
| `--neo4j-password` | `string` | `NEO4J_PASSWORD` | `password` | Neo4j authentication password. |
| `--neo4j-aura-env` | `path` | -- | -- | Path to a Neo4j Aura `.env` file with `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD`. Automatically sets `neo4j_type` to `aura`. |
| `--neo4j-local` | `flag` | -- | `false` | Use `@johnymontana/neo4j-local` for a lightweight local Neo4j instance (no Docker required, needs Node.js). Sets `neo4j_type` to `local`. |
| `--anthropic-api-key` | `string` | `ANTHROPIC_API_KEY` | -- | Anthropic API key. Enables LLM-powered data generation (realistic entity names, documents, decision traces) and custom domain generation. |
| `--openai-api-key` | `string` | `OPENAI_API_KEY` | -- | OpenAI API key. Used by OpenAI Agents and LangGraph frameworks. |
| `--google-api-key` | `string` | `GOOGLE_API_KEY` | -- | Google/Gemini API key. Required for the `google-adk` framework. A warning is shown during scaffolding if google-adk is selected without this key. |
| `--output-dir` | `path` | -- | `./<project-slug>` | Directory where the generated project is written. Defaults to a kebab-case slug of the project name in the current working directory. |
| `--demo` | `flag` | -- | `false` | Convenience shortcut for `--reset-database --demo-data --ingest`. Scaffolds, generates demo data, clears Neo4j, and ingests everything in one step. |
| `--reset-database` | `flag` | -- | `false` | Clear all existing data from Neo4j before ingesting. Runs `MATCH (n) DETACH DELETE n`. Useful when switching domains on a shared Neo4j instance. |
| `--dry-run` | `flag` | -- | `false` | Preview what would be generated (project config summary) without creating any files. |
| `--verbose` | `flag` | -- | `false` | Enable verbose debug logging during generation. Useful for troubleshooting. |
| `--list-domains` | `flag` | -- | -- | Print all available domain IDs and names, then exit. |
| `--version` | `flag` | -- | -- | Print the installed version and exit. |
| `--help` | `flag` | -- | -- | Show the help message and exit. |

## Interactive vs. Non-Interactive Mode

The CLI operates in two modes:

- **Interactive mode:** If `--domain` or `--framework` is missing, the 7-step interactive wizard launches. The wizard uses [Questionary](https://questionary.readthedocs.io/) prompts to collect all configuration.
- **Non-interactive mode:** If `--domain` (or `--custom-domain`) and `--framework` are both provided, the wizard is skipped entirely. `PROJECT_NAME` is optional — if omitted, a slug is auto-generated from the domain and framework (e.g., `healthcare-pydanticai-app`). This mode is suitable for CI/CD pipelines and scripting.

## Examples

### Interactive wizard

Launch the wizard, which prompts for project name, domain, framework, data source, and Neo4j configuration:

```bash
create-context-graph
```

### Fully non-interactive

Generate a financial services app with PydanticAI and demo data, no prompts:

```bash
create-context-graph my-fintech-app \
  --domain financial-services \
  --framework pydanticai \
  --demo-data
```

### LLM-powered data generation

Generate realistic synthetic data using the Anthropic API:

```bash
create-context-graph healthcare-app \
  --domain healthcare \
  --framework claude-agent-sdk \
  --demo-data \
  --anthropic-api-key sk-ant-...
```

Or using the environment variable:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
create-context-graph healthcare-app \
  --domain healthcare \
  --framework claude-agent-sdk \
  --demo-data
```

### Custom domain from natural language

Describe your domain in plain English and let the LLM generate the ontology:

```bash
create-context-graph vet-clinic \
  --custom-domain "veterinary clinic managing patients, owners, appointments, and treatments" \
  --framework pydanticai \
  --demo-data \
  --anthropic-api-key sk-ant-...
```

### With SaaS connectors

Enable GitHub and Slack data import:

```bash
create-context-graph dev-team-graph \
  --domain software-engineering \
  --framework langgraph \
  --connector github \
  --connector slack
```

### Import chat history from Claude AI or ChatGPT

```bash
create-context-graph my-chat-graph \
  --domain personal-knowledge \
  --framework pydanticai \
  --import-type claude-ai \
  --import-file ~/Downloads/claude-export.zip \
  --import-depth deep \
  --import-filter-after 2025-06-01
```

### Import Linear workspace data

```bash
create-context-graph my-project \
  --domain software-engineering \
  --framework pydanticai \
  --connector linear \
  --linear-api-key lin_api_xxxxx \
  --linear-team ENG
```

### With MCP server for Claude Desktop

Generate a project with MCP server support:

```bash
create-context-graph my-app \
  --domain healthcare \
  --framework pydanticai \
  --demo-data \
  --with-mcp \
  --mcp-profile extended
```

After scaffolding, copy `mcp/claude_desktop_config.json` to your Claude Desktop config directory and restart Claude Desktop to connect.

### Scaffold and ingest into Neo4j

Generate the project, create demo data, and load it into a running Neo4j instance:

```bash
create-context-graph my-app \
  --domain supply-chain \
  --framework openai-agents \
  --demo-data \
  --ingest \
  --neo4j-uri neo4j://localhost:7687 \
  --neo4j-password my-secret
```

### Quick demo (scaffold + seed + ingest in one step)

```bash
create-context-graph my-app \
  --domain healthcare \
  --framework pydanticai \
  --demo \
  --neo4j-uri neo4j://localhost:7687
```

### Reset Neo4j before ingesting

Clear all existing data from a shared Neo4j instance before loading new domain data:

```bash
create-context-graph my-app \
  --domain healthcare \
  --framework pydanticai \
  --demo-data \
  --ingest \
  --reset-database \
  --neo4j-uri neo4j://localhost:7687
```

### Custom output directory

Write the generated project to a specific path:

```bash
create-context-graph my-app \
  --domain healthcare \
  --framework crewai \
  --output-dir /tmp/projects/healthcare-demo
```

### Preview without creating files

```bash
create-context-graph my-app \
  --domain healthcare \
  --framework pydanticai \
  --dry-run
```

### List all available domains

```bash
create-context-graph --list-domains
```

### Using uvx (no install required)

```bash
uvx create-context-graph my-app --domain healthcare --framework pydanticai --demo-data
```

## Environment Variables

The following environment variables are read as defaults for their corresponding CLI options:

| Variable | CLI Option |
|----------|-----------|
| `NEO4J_URI` | `--neo4j-uri` |
| `NEO4J_USERNAME` | `--neo4j-username` |
| `NEO4J_PASSWORD` | `--neo4j-password` |
| `ANTHROPIC_API_KEY` | `--anthropic-api-key` |
| `OPENAI_API_KEY` | `--openai-api-key` |
| `GOOGLE_API_KEY` | `--google-api-key` |
| `LINEAR_API_KEY` | `--linear-api-key` |
| `LINEAR_TEAM` | `--linear-team` |

CLI flags always take precedence over environment variables.
