---
sidebar_position: 4
title: "Decision Traces from Google Workspace"
---

# Decision Traces from Google Workspace

This tutorial walks you through importing your team's Google Workspace data -- Drive files, comment threads, revision history, calendar events, and email metadata -- into a Neo4j context graph. The defining feature is **decision trace extraction**: resolved comment threads in Google Docs become first-class decision nodes in your graph, capturing the question, deliberation, resolution, and participants.

By the end, you'll have an AI agent that can answer questions like "Why did we choose Stripe over Adyen?" by traversing the decision traces embedded in your team's collaborative documents.

## What you'll build

A full-stack application that:

- Imports your Google Drive files, folders, and permissions into Neo4j
- Extracts **resolved comment threads** from Google Docs as decision trace nodes -- capturing who asked, who replied, what was decided, and when
- Maps revision history to show who changed what and when
- Optionally imports Calendar events and Gmail thread metadata for full decision context
- Provides 10 decision-focused agent tools (`find_decisions`, `who_decided`, `open_questions`, etc.)
- Connects Google Workspace decisions to Linear issues when both connectors are active

## Prerequisites

Before you begin, make sure you have:

- **Python 3.11+** -- check with `python --version`
- **Node.js 18+** -- check with `node --version`
- **Neo4j** -- one of:
  - [Neo4j Aura](https://console.neo4j.io) (free cloud instance)
  - Docker: `docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5`
  - neo4j-local: `npx @johnymontana/neo4j-local`
- **uv** (recommended) -- install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Google Cloud project with OAuth credentials** -- see Step 1 below
- **An LLM API key** -- `ANTHROPIC_API_KEY` (for most frameworks) or `OPENAI_API_KEY` / `GOOGLE_API_KEY` depending on your framework choice

## Step 1: Set Up Google Cloud OAuth Credentials

The connector uses OAuth 2.0 to access your Google Workspace data with read-only permissions. You'll need to create OAuth credentials in the Google Cloud Console.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project (or select an existing one).
2. Navigate to **APIs & Services > Library** and enable these APIs:
   - **Google Drive API**
   - **Drive Activity API** (for activity tracking)
   - Optionally: **Google Calendar API** and **Gmail API** (if you plan to import those)
3. Navigate to **APIs & Services > Credentials**.
4. Click **Create Credentials > OAuth client ID**.
5. Select **Desktop app** as the application type.
6. Copy the **Client ID** and **Client Secret** -- you'll use these in the next step.

:::tip
If your Google Workspace has domain-wide restrictions on third-party apps, you may need an admin to approve the OAuth consent screen. For personal Google accounts, this step is automatic.
:::

## Step 2: Scaffold the Project

Run the CLI with the `--connector google-workspace` flag:

```bash
uvx create-context-graph my-decisions-app \
  --domain software-engineering \
  --framework pydanticai \
  --connector google-workspace \
  --gws-folder-id 1aBcDeFgHiJkLmNoPqRsT
```

Replace the folder ID with your target Drive folder. You can find this in the URL when you open the folder in Google Drive: `https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsT`.

:::tip
Targeting a specific folder keeps the graph focused and manageable. For a first import, try your team's PRD or design docs folder -- these tend to have the richest comment threads.
:::

The CLI will open your browser for the Google OAuth consent flow. After granting read-only access, the import begins automatically:

```
Importing data from connected services...
  Connecting to Google Workspace...
  Fetching data from Google Workspace...
  ✓ Google Workspace: 156 entities, 42 documents
```

### Customizing what gets imported

The connector has several flags to control scope:

```bash
uvx create-context-graph my-decisions-app \
  --domain software-engineering \
  --framework pydanticai \
  --connector google-workspace \
  --gws-folder-id 1aBcDeFg \
  --gws-include-calendar \
  --gws-include-gmail \
  --gws-since 2026-01-01 \
  --gws-mime-types docs,slides \
  --gws-max-files 200
```

| Flag | Default | Description |
|------|---------|-------------|
| `--gws-folder-id` | My Drive root | Drive folder ID to scope the import |
| `--gws-include-comments` / `--gws-no-comments` | on | Import comment threads from Docs/Sheets/Slides |
| `--gws-include-revisions` / `--gws-no-revisions` | on | Import revision history metadata |
| `--gws-include-activity` / `--gws-no-activity` | on | Import Drive Activity events |
| `--gws-include-calendar` | off | Import Calendar events (requires Calendar API scope) |
| `--gws-include-gmail` | off | Import Gmail thread metadata (requires Gmail API scope) |
| `--gws-since` | 90 days ago | Only import activity after this ISO date |
| `--gws-mime-types` | `docs,sheets,slides` | Comma-separated MIME types to include |
| `--gws-max-files` | 500 | Maximum number of files to import |

## Step 3: Start Neo4j and Seed the Data

Navigate to your project and seed the data into Neo4j:

```bash
cd my-decisions-app
make seed
```

Configure Neo4j connection details in `.env` if needed:

```bash
# .env
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

## Step 4: Start the Application

```bash
make start
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Step 5: Explore Your Decision Graph

### Schema view

When the app loads, the graph schema view shows the entity types imported from Google Workspace:

- **Document** nodes (your Google Docs, Sheets, and Slides) connected to **Person** nodes via `CREATED_BY` and `SHARED_WITH`
- **DecisionThread** nodes linked to Documents via `HAS_COMMENT_THREAD` -- these are the extracted comment threads
- **Reply** nodes connected to DecisionThreads via `HAS_REPLY` -- the deliberation chain
- **Revision** nodes showing document evolution via `HAS_REVISION` and `REVISED_BY`
- **Activity** nodes tracking actions (edits, shares, renames) via `ACTIVITY_ON` and `PERFORMED_BY`
- **Folder** nodes providing hierarchy via `CONTAINED_IN`
- **Meeting** nodes (if calendar was enabled) linked to Documents via `DISCUSSED_IN` and to Persons via `ATTENDEE_OF`
- **EmailThread** nodes (if Gmail was enabled) linked to Documents via `THREAD_ABOUT`

Double-click any schema node to load actual instances.

### Decision threads -- the core concept

The key innovation is the **DecisionThread** node. When someone resolves a comment thread in Google Docs, the connector captures it as a graph node with:

- **content**: The original question or proposal ("Should we use SAML or OIDC for SSO?")
- **quotedContent**: The document text the comment is anchored to
- **resolution**: The final answer (from the last reply before resolution)
- **resolved**: `true` for decisions made, `false` for open questions
- **participantCount**: How many people contributed to the discussion

Each DecisionThread is linked to:
- The **Document** it appears in (`HAS_COMMENT_THREAD`)
- The **Person** who started it (`AUTHORED_BY`)
- The **Person** who resolved it (`RESOLVED_BY`)
- Individual **Reply** nodes capturing the deliberation (`HAS_REPLY`)

Resolved threads also generate **decision traces** (the same format used by neo4j-agent-memory) with thought/action/observation steps for each reply in the thread.

### Ask the agent about decisions

Try these questions in the chat panel:

- **"What decisions have been made about authentication?"** -- Searches DecisionThread nodes by keyword
- **"Who was involved in decisions about the caching strategy?"** -- Finds decision participants
- **"Are there any open questions on the API design doc?"** -- Finds unresolved comment threads
- **"What happened in last Tuesday's platform meeting?"** -- Finds meeting context, linked documents, and decisions
- **"Show me the timeline of the payments PRD"** -- Revision history, comment threads, and activity
- **"Who are the top contributors to the architecture docs?"** -- Combines revision, comment, and meeting data
- **"Trace back the decision to use Redis"** -- Follows the decision chain: thread -> document -> meeting
- **"What documents haven't been updated in 30 days but still have open questions?"** -- Finds stale docs with pending decisions
- **"What's everything related to ENG-456?"** -- Cross-references Linear issues (if Linear connector is also active)

### Graph visualization

As you chat with the agent, the graph visualization updates in real-time showing the queried nodes and relationships:

- **Double-click** a DecisionThread node to see its replies and participants
- **Double-click** a Document to see its comment threads, revisions, and activity
- **Click** any node to inspect its properties in the detail panel
- Use the **"Ask about this"** button to query a specific entity

## Understanding the Graph Schema

### Entity types

| Google Workspace Concept | Graph Label | POLE Type | Key Properties |
|---|---|---|---|
| File (Doc/Sheet/Slide) | `Document` | Object | name, mimeType, driveId, webViewLink, createdTime, modifiedTime |
| Folder | `Folder` | Object | name, driveId, parentId |
| User | `Person` | Person | displayName, emailAddress |
| Comment thread | `DecisionThread` | Object | content, resolved, resolution, quotedContent, participantCount |
| Comment reply | `Reply` | Object | content, createdTime |
| Revision | `Revision` | Event | revisionId, modifiedTime |
| Drive action | `Activity` | Event | actionType, timestamp, targetName |
| Calendar event | `Meeting` | Event | summary, startTime, endTime, attendeeCount |
| Email thread | `EmailThread` | Object | subject, messageCount, participantEmails |

### Relationship types

| Relationship | From | To | Meaning |
|---|---|---|---|
| `HAS_COMMENT_THREAD` | Document | DecisionThread | Comment thread on a document |
| `HAS_REPLY` | DecisionThread | Reply | Reply in a discussion |
| `AUTHORED_BY` | DecisionThread/Reply | Person | Who wrote the comment |
| `RESOLVED_BY` | DecisionThread | Person | Who resolved the thread (made the decision) |
| `HAS_REVISION` | Document | Revision | Document edit history |
| `REVISED_BY` | Revision | Person | Who made the edit |
| `ACTIVITY_ON` | Activity | Document | Action performed on a file |
| `PERFORMED_BY` | Activity | Person | Who performed the action |
| `CONTAINED_IN` | Document | Folder | Folder hierarchy |
| `CREATED_BY` | Document | Person | File owner |
| `SHARED_WITH` | Document | Person | File permission |
| `ATTENDEE_OF` | Person | Meeting | Meeting attendee |
| `ORGANIZED_BY` | Meeting | Person | Meeting organizer |
| `DISCUSSED_IN` | Document | Meeting | Doc linked from event |
| `PARTICIPANT_IN` | Person | EmailThread | Email participant |
| `THREAD_ABOUT` | EmailThread | Document | Email references a doc |
| `RELATES_TO_ISSUE` | DecisionThread/Document | Issue | Cross-connector: references a Linear issue |

## Combining with Linear for the Full Decision Lifecycle

The real power emerges when you combine Google Workspace with the Linear connector. Together, they create a complete decision lifecycle graph:

```bash
uvx create-context-graph my-full-context-app \
  --domain software-engineering \
  --framework pydanticai \
  --connector google-workspace \
  --connector linear \
  --gws-folder-id 1aBcDeFg \
  --gws-include-calendar \
  --linear-api-key lin_api_xxxxx
```

Now the agent can traverse the full chain:

1. **Meeting** (Calendar): "Platform team sync" where caching was discussed
2. **Document** (Drive): "Caching Strategy PRD" that was on the agenda
3. **DecisionThread** (Comments): "Should we use Redis?" resolved with "Yes, agreed"
4. **Issue** (Linear): ENG-456 implementing the caching layer

The connector automatically detects Linear issue references (like `ENG-456`) in comment bodies, document names, email subjects, and meeting descriptions, and creates `RELATES_TO_ISSUE` relationships to link the decision context to the execution context.

Try asking the agent:

- **"What decisions were made about ENG-456?"** -- Traverses from the Linear issue to Google Docs decisions
- **"Show me everything related to the API redesign"** -- Finds Linear issues, Docs, comment threads, meetings, and emails
- **"What meetings led to the decision to use microservices?"** -- Traces from DecisionThread back to Meeting via Document

## Example Cypher Queries

Run these in Neo4j Browser (`http://localhost:7474`) or via the agent's `run_cypher` tool:

### Find all resolved decisions about a topic

```cypher
MATCH (dt:DecisionThread {resolved: true})-[:HAS_COMMENT_THREAD]-(doc:Document)
WHERE toLower(dt.content) CONTAINS 'caching'
   OR toLower(doc.name) CONTAINS 'caching'
OPTIONAL MATCH (dt)-[:AUTHORED_BY]->(author:Person)
OPTIONAL MATCH (dt)-[:RESOLVED_BY]->(resolver:Person)
RETURN dt.content AS question, dt.resolution AS decision,
       author.name AS raised_by, resolver.name AS decided_by,
       doc.name AS document
```

### Who makes the most decisions?

```cypher
MATCH (p:Person)<-[:RESOLVED_BY]-(dt:DecisionThread {resolved: true})
RETURN p.name, p.emailAddress, count(dt) AS decisions_resolved
ORDER BY decisions_resolved DESC
LIMIT 10
```

### Open questions across all documents

```cypher
MATCH (dt:DecisionThread {resolved: false})-[:HAS_COMMENT_THREAD]-(doc:Document)
OPTIONAL MATCH (dt)-[:AUTHORED_BY]->(author:Person)
RETURN dt.content AS question, doc.name AS document,
       author.name AS raised_by, dt.createdTime AS since
ORDER BY dt.createdTime DESC
```

### Document evolution timeline

```cypher
MATCH (doc:Document {name: 'Caching Strategy PRD'})
OPTIONAL MATCH (doc)-[:HAS_REVISION]->(rev:Revision)-[:REVISED_BY]->(reviser:Person)
OPTIONAL MATCH (doc)-[:HAS_COMMENT_THREAD]->(dt:DecisionThread)
RETURN doc.name,
       collect(DISTINCT {type: 'revision', time: rev.modifiedTime, by: reviser.name}) AS revisions,
       collect(DISTINCT {type: 'decision', content: dt.content, resolved: dt.resolved}) AS decisions
```

### Meetings where a document was discussed

```cypher
MATCH (doc:Document)-[:DISCUSSED_IN]->(m:Meeting)
OPTIONAL MATCH (m)<-[:ATTENDEE_OF]-(p:Person)
RETURN m.summary, m.startTime, doc.name,
       collect(DISTINCT p.name) AS attendees
ORDER BY m.startTime DESC
```

### Cross-connector: decisions about a Linear issue

```cypher
MATCH (dt:DecisionThread)-[:RELATES_TO_ISSUE]->(issue)
WHERE issue.name CONTAINS 'ENG-456'
MATCH (dt)-[:HAS_COMMENT_THREAD]-(doc:Document)
OPTIONAL MATCH (dt)-[:RESOLVED_BY]->(resolver:Person)
RETURN dt.content AS decision, dt.resolution AS outcome,
       doc.name AS document, resolver.name AS decided_by
```

## Re-importing Updated Data

As your team creates new documents and resolves comment threads, re-import to keep the graph current:

```bash
# Re-import from Google Workspace
make import

# Re-import and seed into Neo4j
make import-and-seed
```

For incremental updates, use the `--gws-since` flag to only fetch recent activity:

```bash
python scripts/import_google_workspace.py --sync
```

## Privacy and Security

The Google Workspace connector is designed with privacy in mind:

- **Read-only access**: All OAuth scopes are read-only. Nothing is written back to Google Workspace.
- **Gmail metadata only**: When Gmail import is enabled, only thread metadata (subject, participants, date) is imported -- no email body text.
- **Scoped by folder**: Use `--gws-folder-id` to limit the import to specific folders.
- **Tokens stored locally**: OAuth tokens are saved to `.gws-token.json` in your project directory and are included in `.gitignore`.
- **No external dependencies**: The connector uses Python's built-in `urllib` -- no third-party API client libraries required at runtime.

## Next Steps

- **Add Linear for full decision lifecycle** -- Combine `--connector google-workspace --connector linear` to link decisions to execution
- **Enable Calendar and Gmail** -- Add `--gws-include-calendar --gws-include-gmail` for meeting context and email threads
- **Customize agent tools** -- Edit the generated `agent.py` to add domain-specific Cypher queries
- **Set up periodic sync** -- Run `make import-and-seed` on a schedule to keep the graph fresh
- **Explore the [How Decision Traces Work](/docs/explanation/how-decision-traces-work) explainer** for the conceptual model behind decision extraction
