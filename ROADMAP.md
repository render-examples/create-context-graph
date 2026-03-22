# Roadmap — Create Context Graph

> Last updated: March 22, 2026

## Overview

Create Context Graph is being built in 5 phases over ~12 weeks. The goal is to go from an empty repository to a published CLI tool that generates domain-specific context graph applications for 22 industry verticals with 8 agent framework options.

---

## Phase 1: Core CLI & Template Engine — COMPLETE

**Timeline:** Weeks 1–3
**Status:** Done

Built the foundational scaffolding tool: Python package structure, CLI, interactive wizard, template engine, and initial templates.

### What was built

- **Python package** (`src/create_context_graph/`) with `hatchling` build, `src` layout, entry point via `create-context-graph` command
- **Click CLI** (`cli.py`) with both interactive and non-interactive (flag-based) modes
- **Interactive wizard** (`wizard.py`) — 7-step flow using Questionary + Rich: project name, data source, domain selection, agent framework, Neo4j connection, API keys, confirmation
- **ProjectConfig model** (`config.py`) — Pydantic model holding all wizard outputs, computed slug, framework display names and dependency mappings for all 8 planned frameworks
- **Domain ontology system** (`ontology.py`) — YAML loader with two-layer inheritance (`_base.yaml` + domain YAML), Pydantic validation models for all ontology sections, code generation helpers (Cypher schema, Pydantic models, NVL visualization config)
- **Jinja2 template engine** (`renderer.py`) — `PackageLoader`-based renderer with custom filters (`snake_case`, `camel_case`, `pascal_case`, `kebab_case`), renders full project directory from templates + ontology context
- **3 initial domain ontologies** — Financial Services, Healthcare, Software Engineering (complete with entity types, relationships, document templates, decision traces, demo scenarios, agent tools, system prompts, visualization config)
- **Backend templates** — FastAPI main, config, Neo4j client, GDS client, vector search client, Pydantic models, REST routes, pyproject.toml, data generation script, agent stub fallback
- **2 agent framework templates** — PydanticAI (structured tool definitions with `RunContext`) and Claude Agent SDK (Anthropic tool-use with agentic loop)
- **Frontend templates** — Next.js 15 + Chakra UI v3 + NVL: layout, page (3-panel), ChatInterface, ContextGraphView, DecisionTracePanel, Provider, domain config, theme
- **Base templates** — `.env`, `Makefile`, `docker-compose.yml`, `README.md`, `.gitignore`
- **Cypher templates** — Schema constraints/indexes from ontology, GDS graph projections
- **Neo4j connection validator** (`neo4j_validator.py`)

### Key design decisions made

- Templates are **domain-agnostic, data-driven** — no per-domain template directories; the ontology YAML drives all customization
- Only `agent.py` varies by framework; everything else is shared
- JSX/Python dict literals in templates use `{% raw %}...{% endraw %}` blocks to avoid Jinja2 conflicts
- Pre-built fixtures are bundled and copied into every generated project

---

## Phase 2: Domain Expansion & Document Generation — COMPLETE

**Timeline:** Weeks 4–6
**Status:** Done

Expanded from 3 domains to 22, built the synthetic data generation pipeline, and created the Neo4j ingestion system.

### What was built

- **19 additional domain ontology YAMLs** — All validated and scaffold-tested. Domains: Agent Memory, Conservation, Data Journalism, Digital Twin, Gaming, GenAI/LLM Ops, GIS & Cartography, Golf & Sports Mgmt, Hospitality, Manufacturing, Oil & Gas, Personal Knowledge, Product Management, Real Estate, Retail & E-Commerce, Scientific Research, Trip Planning, Vacation Industry, Wildlife Management
- **Synthetic data generation pipeline** (`generator.py`) — 4-stage pipeline:
  1. **Entity seeding** — LLM-powered or static fallback, generates 5+ entities per type with properties matching ontology schema
  2. **Relationship weaving** — Connects entities based on ontology relationship definitions, avoids self-relationships
  3. **Document generation** — Produces 25+ documents across all template types defined in the ontology (LLM-powered for realistic content, static fallback for offline use)
  4. **Decision trace injection** — Creates reasoning traces from ontology scenarios with thought/action/observation steps
- **LLM client abstraction** — Supports both Anthropic and OpenAI as generation providers, graceful fallback to static data when no API key is available
- **Data ingestion system** (`ingest.py`) — Dual-backend ingestion:
  - Primary: `neo4j-agent-memory` MemoryClient (long-term entities, short-term documents, reasoning traces — all three memory types)
  - Fallback: Direct `neo4j` driver when neo4j-agent-memory isn't installed
  - Schema application from generated Cypher
- **Pre-generated fixture files** — All 22 domains ship with static `fixtures/{domain-id}.json` files so projects work immediately without an LLM API key
- **CLI integration** — `--demo-data` flag triggers generation, `--ingest` flag triggers Neo4j ingestion, `--anthropic-api-key` enables LLM-powered generation, pre-built fixtures always copied into `data/fixtures.json`
- **Comprehensive test suite** (85 tests, all passing):
  - `test_config.py` — 10 unit tests for ProjectConfig
  - `test_ontology.py` — 20 unit tests including parametric validation of all 22 domains
  - `test_renderer.py` — 18 unit tests for rendering, file structure, framework selection, Python compile verification
  - `test_generator.py` — 14 unit tests for data generation across 6 domains
  - `test_cli.py` — 13 integration tests for CLI invocation, 6 domain/framework combinations

### Verified

- All 22 domains load and validate without errors
- 18/18 domain+framework combinations scaffold successfully (9 domains x 2 frameworks)
- Generated Python files pass `compile()` syntax check
- 85/85 tests pass in 3.4 seconds

---

## Phase 3: Framework Templates & Frontend — COMPLETE

**Timeline:** Weeks 7–8
**Status:** Done

Added all 8 agent framework templates, replaced NVL placeholder with real graph visualization, and expanded the test suite.

### What was built

- **6 new agent framework templates** — All in `templates/backend/agents/`, each generating valid Python with domain-specific tools from ontology:
  - **OpenAI Agents SDK** (`openai_agents/`) — `@function_tool` decorators + `Runner.run()`
  - **LangGraph** (`langgraph/`) — `@tool` + `create_react_agent()` with `ChatAnthropic`
  - **CrewAI** (`crewai/`) — `Agent` + `Task` + `Crew` with `@tool` decorator
  - **Strands (AWS)** (`strands/`) — `Agent` with `@tool`, Bedrock model
  - **Google ADK** (`google_adk/`) — `Agent` + `FunctionTool`, Gemini model, async runner
  - **MAF** (`maf/`) — Modular tool registry with decorator pattern
- **NVL graph visualization** — Replaced placeholder in `ContextGraphView.tsx` with real `@neo4j-nvl/react` `InteractiveNvlWrapper` component: force-directed layout, domain-colored nodes via `NODE_COLORS`/`NODE_SIZES`, node click handler, color legend
- **Makefile improvements** — Added `make test` and `make lint` targets
- **Expanded test suite** (103 tests, all passing in 3.78s):
  - `TestAllFrameworksRender` — 8 parametric tests verifying each framework's agent.py compiles and contains framework-specific imports
  - `TestAllFrameworksRender` — 8 parametric tests verifying each framework's pyproject.toml contains correct dependencies
  - `TestMultipleDomainScaffolds` — Expanded from 6 to 8 domain/framework combinations covering all frameworks

### Verified

- All 8 frameworks scaffold, render, and compile without errors
- All 8 frameworks produce correct `pyproject.toml` dependencies
- Each framework's agent.py contains the expected framework marker (import/class name)
- 103/103 tests pass in 3.78 seconds

---

## Phase 4: SaaS Import & Custom Domains — COMPLETE

**Timeline:** Weeks 9–10
**Status:** Done

Implemented SaaS data connectors for 7 services and LLM-powered custom domain generation.

### What was built

#### SaaS data connectors

- **Connectors package** (`connectors/`) — `BaseConnector` ABC, `NormalizedData` Pydantic model matching fixture schema, connector registry with `@register_connector` decorator
- **7 service connectors**, each with `authenticate()`, `fetch()`, and `get_credential_prompts()`:

| Service | Connector | Auth Method | Dependencies |
|---------|-----------|-------------|-------------|
| GitHub | `github_connector.py` | Personal access token | PyGithub |
| Notion | `notion_connector.py` | Integration token | notion-client |
| Jira | `jira_connector.py` | API token | atlassian-python-api |
| Slack | `slack_connector.py` | Bot OAuth token | slack-sdk |
| Gmail | `gmail_connector.py` | gws CLI or OAuth2 | google-api-python-client, google-auth-oauthlib |
| Google Calendar | `gcal_connector.py` | gws CLI or OAuth2 | google-api-python-client, google-auth-oauthlib |
| Salesforce | `salesforce_connector.py` | Username/password + security token | simple-salesforce |

- **Google Workspace CLI (`gws`) integration** — Gmail and Google Calendar connectors detect `gws` on PATH, offer to install via npm if missing, fall back to Python OAuth2
- **OAuth2 local redirect flow** (`oauth.py`) — Temporary HTTP server on random port, browser consent, auth code capture, token exchange
- **Dual-purpose connectors** — Run at scaffold time to populate initial data AND generated into the scaffolded project for ongoing `make import` / `make import-and-seed` usage
- **Connector templates** — 7 standalone connector `.py.j2` templates + `import_data.py.j2` generated into scaffolded projects (only for selected connectors)
- **Makefile targets** — `make import` and `make import-and-seed` added to generated projects when SaaS connectors are selected
- **Wizard integration** — Checkbox selection of connectors, credential prompts, gws CLI detection and install prompt
- **CLI flags** — `--connector` (multiple) for non-interactive connector selection
- **Optional dependencies** — New `[connectors]` extra in pyproject.toml

#### Custom domain generation

- **`custom_domain.py`** — LLM-powered domain YAML generation:
  1. Loads `_base.yaml` + 2 reference domain YAMLs (healthcare, wildlife-management) as few-shot examples
  2. Builds prompt with complete YAML schema specification
  3. Calls LLM (Anthropic/OpenAI) via existing `generator.py` abstraction
  4. Parses YAML, validates against `DomainOntology` Pydantic model
  5. On validation failure, retries with error feedback (up to 3 attempts)
  6. Returns `(DomainOntology, raw_yaml_string)`
- **`ontology.py` extensions** — `load_domain_from_yaml_string()`, `load_domain_from_path()`, `list_available_domains()` now scans `~/.create-context-graph/custom-domains/`
- **Wizard integration** — Description prompt → LLM generation with spinner → Rich summary table → accept/regenerate/edit → optional save for reuse
- **CLI flag** — `--custom-domain "description"` for non-interactive custom domain generation
- **Renderer support** — Custom domain YAML written directly to `data/ontology.yaml`
- **Persistence** — Custom domains saved to `~/.create-context-graph/custom-domains/` and appear in future wizard runs

### Bug fixes

- Fixed `cli.py:73` — `data_source` was always `"demo"` regardless of flags

### Tests added (40 new tests)

- `test_custom_domain.py` — 17 tests: YAML string loading, base merge, validation errors, prompt construction, mocked LLM generation (success, retry, max retries), display, save, custom domain listing
- `test_connectors.py` — 23 tests: NormalizedData model, merge, registry (7 connectors), credential prompts, mocked fetch for GitHub/Notion/Jira/Slack/Gmail/GCal/Salesforce, OAuth helpers

### Verified

- All 7 connectors register and expose credential prompts
- Mocked connector fetches return valid NormalizedData
- Custom domain generation succeeds with mocked LLM
- Custom domain retry loop works on validation failure
- 182/182 tests pass in 5.2 seconds

---

## Phase 5: Polish, Testing & Launch — NOT STARTED

**Timeline:** Weeks 11–12
**Status:** Planned

### Goals

Prepare for public release: comprehensive testing, documentation, and publishing.

### Planned work

#### End-to-end testing

- CI matrix: all 22 domains x 2 frameworks (PydanticAI + Claude Agent SDK) minimum
- Extended matrix: spot-check remaining frameworks
- Verify: directory structure, valid Python syntax, valid TypeScript/JSX syntax, Cypher syntax
- Timed test: generation completes in < 2 minutes per domain
- Smoke test: generated app starts and responds to health check (requires Neo4j in CI)

#### Documentation (Diataxis framework)

| Type | Page | Description |
|------|------|-------------|
| Tutorial | Your First Context Graph App | Step-by-step: install, run wizard, explore the generated app |
| Tutorial | Customizing Your Domain Ontology | Modify a generated ontology and re-seed data |
| How-To | Import Data from Gmail & Slack | Connect SaaS services and import real data |
| How-To | Add a Custom Domain | Use the Custom option or write ontology YAML manually |
| How-To | Switch Agent Frameworks | Regenerate with a different framework, preserving data |
| Reference | CLI Options & Flags | Complete reference for all CLI arguments |
| Reference | Ontology YAML Schema | Schema definition for domain ontology files |
| Reference | Generated Project Structure | Every file and directory in the output, explained |
| Explanation | How Domain Ontologies Work | Conceptual guide to the ontology-driven generation system |
| Explanation | Why Context Graphs Need All Three Memory Types | Short-term + long-term + reasoning = context graph |

#### Neo4j Labs compliance

- Labs badge in README and all generated READMEs
- Community-support disclaimer
- Apache-2.0 license headers in all source files
- Contribution guidelines (CONTRIBUTING.md)

#### Publishing

- **PyPI:** GitHub Actions workflow triggered on version tags, publishes to PyPI
- **npm:** GitHub Actions workflow publishes npm-wrapper on the same tag
- **Versioning:** Both packages use the same version, bumped together

### Success metrics

| Metric | Target |
|--------|--------|
| Time to running app | < 5 minutes (excluding Neo4j provisioning) |
| Domain coverage | 22 domains at launch |
| Framework coverage | 8 agent frameworks at launch |
| Generation success rate | >= 95% first-attempt success across all domain x framework combinations |
| Test suite | 100+ tests, all passing |

---

## Summary

| Phase | Description | Status | Tests |
|-------|-------------|--------|-------|
| 1 | Core CLI & Template Engine | **Complete** | 182 passing |
| 2 | Domain Expansion & Data Generation | **Complete** | (included above) |
| 3 | Framework Templates & Frontend | **Complete** | (included above) |
| 4 | SaaS Import & Custom Domains | **Complete** | (included above) |
| 5 | Polish, Testing & Launch | Not started | — |
