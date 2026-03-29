# Changelog

## v0.6.1 — Stability, Data Quality & Tool Coverage (2026-03-28)

### Critical Bug Fixes
- **CrewAI dependency fix** — Changed `crewai>=0.1` to `crewai[anthropic]>=0.1` in framework dependencies. The crewai agent template uses `llm="anthropic/claude-sonnet-4-20250514"` which requires the anthropic extra. Without it, the generated project crashes on startup with `ImportError: Anthropic native provider not available`.
- **CLI non-interactive mode fix** — The CLI no longer requires a positional `PROJECT_NAME` argument when all flags (`--domain`, `--framework`) are provided. Auto-generates a slug like `healthcare-pydanticai-app`. Also added TTY detection with helpful error messages for CI/CD environments.

### Data Quality Improvements
- **Document Markdown rendering** — Static document content now uses Markdown headings (`##`) instead of RST-style `===`/`---` separators. The DocumentBrowser component renders content with ReactMarkdown.
- **Entity-derived document titles** — Document titles now reference primary entities: "Discharge Summary: Maria Elena Gonzalez" instead of generic "Discharge Summary #1".
- **Realistic entity descriptions** — Replaced generic "Comprehensive patient profile for..." with POLE-type-aware descriptions using domain roles and industries (e.g., "Dr. Sarah Chen, attending physician specializing in healthcare").
- **Domain-aware Organization.industry** — Added `DOMAIN_INDUSTRY_POOL` for all 22 domains. Healthcare organizations get "Hospital Systems" instead of "Technology".
- **Realistic decision trace observations** — Observations now reference actual entity names: "Verified Dr. Sarah Chen against healthcare standards" instead of generic "Found 7 relevant records".
- **Improved thinking text filter** — Added continuation patterns to catch multi-sentence agent thinking blocks between tool calls.

### New Agent Tools (All 22 Domains)
- **`list_*` tools** — Every domain now has a list tool for its primary entity type (e.g., `list_patients`, `list_players`, `list_accounts`) with sort and limit parameters.
- **`get_*_by_id` tools** — Every domain now has a direct ID lookup tool that returns the entity with all connections (e.g., `get_patient_by_id`, `get_player_by_id`).
- **Gaming-specific** — Added `get_top_players` tool (sort by level) for the gaming domain.

### Frontend Improvements
- **"Ask about this" button** — Clicking a node in the Knowledge Graph shows an "Ask about [entity]" button that sends a query to the chat.
- **Node hover tooltips** — Graph nodes show full name, labels, and key properties on hover.
- **Health polling optimization** — Reduced polling frequency from 30s to 60s.
- **Responsive hint text** — Keyboard shortcut hint hidden on small screens to prevent overlap.
- **Suggested question max width** — Pill buttons capped at 320px to prevent layout stretching.
- **Scrollable label badges** — Label filter badges in the graph panel scroll when they overflow.
- **Seed constraint fix** — Entity seeding now uses `ON CREATE SET / ON MATCH SET` to avoid constraint violations on re-seed.

### Documentation
- **4 new docs pages** — "Use Neo4j Aura", "Use Docker", "Why Context Graphs?", "Framework Comparison"
- **Updated sidebars** — All new pages added to Docusaurus navigation

### Testing
- 602 passing tests (57 new), up from 545

## v0.6.0 — Comprehensive Testing Feedback (2026-03-28)

### Framework Fixes
- **CrewAI no longer hangs** — Added explicit `llm="anthropic/claude-sonnet-4-20250514"` to prevent defaulting to OpenAI. Added request-level logging and reduced timeout to 60s.
- **Strands serialization fix** — Added `_extract_text()` helper that robustly extracts text from agent results, handling `ParsedTextBlock` serialization issues from newer Anthropic SDK versions.
- **Google ADK API key support** — Added `--google-api-key` CLI flag (`GOOGLE_API_KEY` env), wizard prompt when google-adk is selected, and `GOOGLE_API_KEY` in generated `.env`/`.env.example` templates.

### Document & Trace Ingestion Fix
- **`--ingest` now creates proper Document and DecisionTrace nodes** — Both ingestion paths now create `:Document` and `:DecisionTrace`/`:TraceStep` nodes using direct Cypher, matching the `generate_data.py` pattern that the frontend expects. Previously, Documents and Decision Traces panels appeared empty after `--ingest`.
- **Entity MERGE fix** — Direct driver ingestion now uses `MERGE (n:Label {name: $name}) SET ...` instead of `MERGE (n:Label {all_props})`, preventing duplicate nodes.

### Data Quality
- **Domain-aware base entities** — Person, Organization, Location, Event, and Object entities now use domain-specific names and roles (doctors for healthcare, traders for finance, game designers for gaming, etc.).
- **Fixed templated property values** — Properties like "Metformin 500mg - Contraindications" now replaced with realistic values. Added pools for contraindications, dosage_form, allergies, sector, lead_reporter, manufacturer, mechanism_of_action, population_trend, and habitat.

### Frontend UI Improvements
- **Redesigned chat input** — Bordered container with focus highlight and keyboard shortcut hint (Chakra UI Pro inspired).
- **Suggested questions redesign** — Pill-shaped buttons with full text (no 60-char truncation), "Try these" label with Sparkles icon.
- **Message avatars** — User and assistant messages now have Circle avatars with User/Bot icons.
- **Tool progress counter** — Shows "Running tool N of M..." during tool execution.

### CLI
- **`--demo` convenience flag** — Shortcut for `--reset-database --demo-data --ingest`
- **`--google-api-key` flag** — New CLI flag with `GOOGLE_API_KEY` env variable support

### Testing
- 545 passing tests (35 new), up from 510

## v0.5.2 — Agent Framework Refinements (2026-03-26)

- Improved Anthropic Tools and Claude Agent SDK agent templates
- Enhanced `context_graph_client` event handling and error recovery
- ChatInterface component improvements
- Better error handling in API routes
- `generate_data.py` improvements for data quality
- 74 new ontology validation tests

## v0.5.1 — UX Improvements & Bug Fixes (2026-03-25)

### Bug Fixes
- SSR hydration fix in frontend components
- PydanticAI tool serialization fix — agent tools now return JSON string types correctly
- Google ADK hyphenated domain name sanitization
- HuggingFace warning suppression in agent templates

### Improvements
- Retry button on chat errors
- Agent thinking text collapsible filter — reasoning steps render in a collapsible "Show reasoning" section
- Strands `max_tokens` configuration support
- Cypher query validation tests across all 22 domains

## v0.5.0 — Data Quality & Domain Completeness (2026-03-24)

### New Features
- **22 complete domain ontologies** with pre-generated LLM fixture data shipped for all domains
- **Domain-specific static name pools** — 200+ realistic names across 50+ entity labels (medical diagnoses, financial instruments, software repos, etc.)
- Label-aware ID prefixes (`PAT-` for Patient, `ACT-` for Account, etc.)
- 12+ domain-specific property pools (currency codes, ticker symbols, drug classes, medical specialties, severities)
- `domain` property on all ingested entities for cross-domain isolation when sharing a Neo4j instance
- Structured document templates for static fallback data generation

### Bug Fixes
- Fixed missing SSE event messages in chat streaming
- Float value clamping for confidence/rating/efficiency fields

### Testing
- 510 passing tests (145 new), up from 365

## v0.4.6 — Conversation Fetching Fix (2026-03-24)

- Fixed conversation history fetching in `context_graph_client` for multi-turn sessions

## v0.4.5 — Framework & Build Fixes (2026-03-24)

- Fixed `pyproject.toml` build configuration bug
- Strands framework default changed from Bedrock to AnthropicModel
- Agent template improvements across multiple frameworks
- Domain YAML fixes for gaming, genai-llm-ops, healthcare, personal-knowledge, product-management, retail-ecommerce, software-engineering, and trip-planning

## v0.4.4 — Strands Model Default (2026-03-24)

- Changed Strands agent framework default from AWS Bedrock to Anthropic native model (`AnthropicModel`)

## v0.4.3 — API Keys & Docker Support (2026-03-23)

- Fixed API key handling and validation across agent frameworks
- Added `Dockerfile.backend` template for Docker builds
- Makefile improvements for containerized deployments

## v0.4.2 — E2E Testing & Bug Fixes (2026-03-23)

- Bug fixes across agent templates
- Playwright e2e test scaffolding for generated projects (`app.spec.ts`, `playwright.config.ts`)
- Improved e2e smoke testing infrastructure

## v0.4.1 — Streaming & E2E Infrastructure (2026-03-23)

- **Server-Sent Events (SSE) streaming** for real-time chat responses and tool call visualization
- `POST /chat/stream` endpoint with `asyncio.Queue`-based event streaming
- Token-by-token text streaming for PydanticAI, Anthropic Tools, Claude Agent SDK, OpenAI Agents, LangGraph
- Real-time tool call events with Timeline/Spinner/Collapsible UI components
- Text delta batching (~50ms) to optimize React re-renders
- E2E smoke testing infrastructure (`scripts/e2e_smoke_test.py`)
- Documentation updates

## v0.4.0 — Hardening, Security & DX (2026-03-23)

### Bug Fixes
- **Critical:** Enum identifier sanitization — special characters (`A+`, `A-`, `3d_model`) in domain ontology enum values now generate valid Python identifiers with value aliases
- **Critical:** Graceful degradation when Neo4j is unavailable — backend starts in degraded mode, `/health` endpoint reports connectivity status
- **High:** Cypher injection prevention in GDS client — label parameters validated against entity type whitelist
- **High:** CrewAI async/sync deadlock resolved — replaced bare `asyncio.run()` with `nest_asyncio`-compatible helper, crew execution moved to thread
- **High:** Claude Agent SDK model version now configurable via `ANTHROPIC_MODEL` environment variable
- **Medium:** Silent exception swallowing replaced with structured warning messages in `ingest.py` and `vector_client.py`
- **Medium:** JSON parsing errors in agent tool calls now return helpful error messages instead of crashing
- **Medium:** Input validation (`max_length`) added to chat and search request models
- **Low:** CLI validates empty project names before entering wizard
- **Low:** Healthcare YAML blood type enums properly quoted

### New Features
- `--dry-run` CLI flag — preview what would be generated without creating files
- `--verbose` CLI flag — enable debug logging during generation
- `/health` endpoint in generated projects — returns Neo4j connectivity status and app version
- CORS origins configurable via `CORS_ORIGINS` environment variable
- `constants.py` module in generated projects — centralizes magic strings (index names, graph projections, embedding dimensions)
- Document browser pagination (page size 20, prev/next controls)
- Semantic HTML landmarks (`<main>`, `<section>`, `<aside>`) and ARIA labels in frontend
- Actionable error messages in chat interface — distinguishes backend errors, network failures, and Neo4j unavailability

### Security
- Query timeouts (30s default) on all Neo4j operations
- Credential warnings in generated `.env.example`
- CORS production configuration guidance

### Testing
- 365 passing tests (51 new), up from 314
- New: enum identifier sanitization edge cases
- New: models.py compilation across all 22 domains (prevents enum regression)
- New: v0.4.0 feature validation (health endpoint, constants, graceful degradation, input validation, CORS, pagination)
- New: CLI validation and flag tests

## v0.3.0 — Memory Integration, Multi-Turn & Graph Visualization (2026-03-23)

- neo4j-agent-memory integration for multi-turn conversations
- Interactive NVL graph visualization (schema view, double-click expand, drag/zoom, property panel)
- LLM-generated demo data (80-90 entities, 25+ documents, 3-5 decision traces per domain)
- Markdown rendering in chat with tool call visualization
- Document browser and entity detail panel
- Improved graph visualization and frontend styling
- Docusaurus documentation site setup and deployment
- Improved domain fixture data quality
- 314 passing tests

## v0.2.0 — Connectors & Custom Domains (2026-03-22)

### New Features
- **7 SaaS data connectors** — GitHub, Notion, Jira, Slack, Gmail, Google Calendar, Salesforce
- Each connector implements `BaseConnector` ABC with `authenticate()`, `fetch()`, and `get_credential_prompts()`
- Gmail/Google Calendar prefer `gws` CLI with Python OAuth2 fallback
- **Custom domain generation** — generate complete domain ontology YAMLs from natural language descriptions using LLM (Anthropic/OpenAI)
- Custom domains saved to `~/.create-context-graph/custom-domains/` for reuse
- Neo4j Aura `.env` import and `neo4j-local` support in wizard
- Documentation site (Docusaurus) with deployment configuration

## v0.1.1 — Initial Bug Fixes (2026-03-22)

- Bug fixes for CLI and template rendering
- Test improvements and expanded coverage
- Added `.gitignore` to generated projects

## v0.1.0 — Initial Release (2026-03-22)

- Interactive CLI scaffolding tool (`create-context-graph`) invoked via `uvx` or `npx`
- 7-step interactive wizard with Questionary prompts
- **8 agent frameworks:** PydanticAI, Claude Agent SDK, OpenAI Agents SDK, LangGraph, CrewAI, Strands, Google ADK, Anthropic Tools
- Domain ontology system with YAML definitions and two-layer inheritance (`_base.yaml`)
- Jinja2 template engine generating full-stack projects (FastAPI backend, Next.js + Chakra UI v3 frontend)
- Neo4j schema generation (constraints + GDS projections)
- Static and LLM-powered synthetic data generation pipeline
- Neo4j data ingestion via `neo4j-agent-memory` or direct driver fallback
- Domain-specific agent tools with Cypher queries
- NVL graph visualization component
