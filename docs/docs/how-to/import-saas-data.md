---
sidebar_position: 1
title: Import Data from SaaS Services
---

# Import Data from SaaS Services

Create Context Graph can pull data from SaaS services and map it into your Neo4j knowledge graph. This guide covers how to configure connectors during project scaffolding and how to re-import data afterward.

## Available Connectors

| Service | What It Imports | Auth Method |
|---------|----------------|-------------|
| **GitHub** | Repositories, issues, pull requests, commits, users, code reviews | Personal access token (PAT) |
| **Notion** | Pages, databases, blocks, users, comments | Internal integration token |
| **Jira** | Projects, issues, sprints, users, comments, worklogs | API token + Atlassian email |
| **Slack** | Channels, messages, threads, users, reactions | Bot token (OAuth) |
| **Gmail** | Emails, threads, contacts, labels, attachments (metadata) | Google OAuth 2.0 / service account |
| **Google Calendar** | Events, attendees, calendars, recurring series | Google OAuth 2.0 / service account |
| **Salesforce** | Accounts, contacts, opportunities, leads, cases, activities | OAuth 2.0 connected app |
| **Linear** | Issues, projects, cycles, teams, users, labels, comments, milestones, initiatives, attachments + decision traces | Personal API key |
| **Google Workspace** | Drive files, comment threads (as decision traces), revisions, Drive Activity, Calendar events, Gmail metadata | Google OAuth 2.0 |

## Selecting Connectors in the Interactive Wizard

When you run `create-context-graph my-app`, the wizard includes a step to connect SaaS services:

1. Select **"Connect to SaaS services"** when prompted for your data source.
2. Pick one or more connectors from the checklist.
3. Enter the required credentials for each selected connector (tokens, keys, etc.).
4. The scaffolded project will include connector configuration in `.env` and an import pipeline in `backend/scripts/`.

## Non-Interactive CLI Usage

Pass `--connector` flags to skip the wizard:

```bash
create-context-graph my-app \
  --domain software-development \
  --framework pydanticai \
  --connector github \
  --connector slack
```

You can combine `--connector` with any domain and framework flags. Each connector will prompt for its credentials unless they are already set as environment variables.

### Linear example

Import your Linear workspace data into a context graph:

```bash
create-context-graph my-project \
  --domain software-engineering \
  --framework pydanticai \
  --connector linear \
  --linear-api-key lin_api_xxxxx \
  --linear-team ENG
```

The `--linear-team` flag is optional. If omitted, all teams in the workspace are imported.

### Google Workspace example

Import Drive files, comment threads, and revision history from a specific folder:

```bash
create-context-graph my-decisions-app \
  --domain software-engineering \
  --framework pydanticai \
  --connector google-workspace \
  --gws-folder-id 1aBcDeFgHiJkLmNoPqRsT
```

Add Calendar events and Gmail metadata for full decision context:

```bash
create-context-graph my-decisions-app \
  --domain software-engineering \
  --framework pydanticai \
  --connector google-workspace \
  --gws-folder-id 1aBcDeFg \
  --gws-include-calendar \
  --gws-include-gmail \
  --gws-since 2026-01-01
```

### Combining connectors

Use both Google Workspace and Linear for the full decision lifecycle -- from meeting discussion to code execution:

```bash
create-context-graph my-full-context-app \
  --domain software-engineering \
  --framework pydanticai \
  --connector google-workspace \
  --connector linear \
  --gws-folder-id 1aBcDeFg \
  --gws-include-calendar \
  --linear-api-key lin_api_xxxxx
```

The connectors automatically cross-link: Linear issue references found in Google Docs comments or document names create `RELATES_TO_ISSUE` relationships.

## Gmail and Google Calendar Setup

Gmail and Google Calendar connectors use the **Google Workspace CLI (gws)** for OAuth flows. When you select either connector, the wizard checks whether `gws` is installed:

- If found, it uses `gws` to handle the OAuth consent flow and token refresh.
- If not found, the wizard offers to install it automatically (`pip install gws`).
- You can skip the install and provide a service account JSON key file instead.

Both connectors share the same Google Cloud project credentials, so configuring one makes the other available with no extra setup.

## Re-Importing Data in a Generated Project

After scaffolding, the generated project includes Makefile targets for data import:

```bash
# Import data from all configured connectors
make import

# Import data and seed the graph with demo scenarios
make import-and-seed
```

These targets read credentials from the `.env` file in the project root.

## Connector Credential Setup

### GitHub

1. Go to **Settings > Developer settings > Personal access tokens > Tokens (classic)**.
2. Generate a token with `repo`, `read:org`, and `read:user` scopes.
3. Set `GITHUB_TOKEN` in `.env`.

### Notion

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) and create an internal integration.
2. Copy the **Internal Integration Secret**.
3. Share the target pages/databases with your integration.
4. Set `NOTION_TOKEN` in `.env`.

### Jira

1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) and create an API token.
2. Set `JIRA_EMAIL`, `JIRA_API_TOKEN`, and `JIRA_BASE_URL` (e.g., `https://yourorg.atlassian.net`) in `.env`.

### Slack

1. Create a Slack app at [api.slack.com/apps](https://api.slack.com/apps).
2. Add bot token scopes: `channels:history`, `channels:read`, `users:read`, `reactions:read`.
3. Install the app to your workspace and copy the **Bot User OAuth Token**.
4. Set `SLACK_BOT_TOKEN` in `.env`.

### Gmail / Google Calendar

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the Gmail API and/or Google Calendar API.
3. Create OAuth 2.0 credentials (Desktop app type) and download the JSON file.
4. Set `GOOGLE_CREDENTIALS_FILE` in `.env` pointing to the downloaded JSON.

### Salesforce

1. In Salesforce Setup, go to **App Manager** and create a new Connected App.
2. Enable OAuth and select scopes: `api`, `refresh_token`, `offline_access`.
3. Set `SALESFORCE_CLIENT_ID`, `SALESFORCE_CLIENT_SECRET`, `SALESFORCE_USERNAME`, `SALESFORCE_PASSWORD`, and `SALESFORCE_SECURITY_TOKEN` in `.env`.

### Google Workspace

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project (or select an existing one).
2. Navigate to **APIs & Services > Library** and enable: **Google Drive API**, **Drive Activity API**, and optionally **Google Calendar API** and **Gmail API**.
3. Navigate to **APIs & Services > Credentials** and create an **OAuth client ID** (Desktop app type).
4. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`.
5. Optionally set `GWS_FOLDER_ID` to a Drive folder ID to scope the import.

The Google Workspace connector imports files, comment threads (with resolution detection), revision history, Drive Activity, and optionally Calendar events and Gmail thread metadata. Resolved comment threads are extracted as **decision traces** -- the question, deliberation, resolution, and participants are all captured as graph nodes. It also provides 10 decision-focused agent tools (`find_decisions`, `decision_context`, `who_decided`, `open_questions`, etc.).

See the [Decision Traces from Google Workspace](/docs/tutorials/google-workspace-decisions) tutorial for a complete walkthrough.

### Linear

1. Open **Linear Settings > Security & Access > API** (or navigate to `linear.app/settings/api`).
2. Click **Create key** to generate a personal API key.
3. Set `LINEAR_API_KEY` in `.env`.
4. Optionally set `LINEAR_TEAM` to a team URL key (e.g., `ENG`) to limit the import to a single team.

The Linear connector imports 12 entity types: issues, projects, cycles, teams, users, labels, workflow states, comments (with threading and resolution), project updates (with health status), project milestones, initiatives, and attachments. It also imports:

- **Issue relations** -- blocking, blocked-by, related, and duplicate links between issues
- **Threaded comments** -- with reply hierarchy and resolution tracking (who resolved a discussion thread)
- **Decision traces** -- issue history (state transitions, assignment changes, priority changes) is automatically transformed into decision traces with thought/action/observation chains
- **Documents** -- issue descriptions, project update bodies, and Linear Docs are all imported as documents for semantic search

The connector validates team keys during authentication — if you provide an invalid key, it lists the available team keys. It automatically retries on rate limits (HTTP 429) with exponential backoff, and logs warnings when comments or history entries exceed page limits.

No external Python package is required — the connector uses Python's built-in `urllib`.
