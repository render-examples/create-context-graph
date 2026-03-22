"""Unit tests for SaaS data connectors."""

from unittest.mock import MagicMock, patch

import pytest

from create_context_graph.connectors import (
    CONNECTOR_REGISTRY,
    BaseConnector,
    NormalizedData,
    get_connector,
    list_connectors,
    merge_connector_results,
)


# ---------------------------------------------------------------------------
# NormalizedData model tests
# ---------------------------------------------------------------------------


class TestNormalizedData:
    def test_empty_data(self):
        data = NormalizedData()
        assert data.entities == {}
        assert data.relationships == []
        assert data.documents == []

    def test_with_data(self):
        data = NormalizedData(
            entities={"Person": [{"name": "Alice"}]},
            relationships=[{"type": "KNOWS", "source": "Alice", "target": "Bob"}],
            documents=[{"title": "Doc", "content": "Hello"}],
        )
        assert len(data.entities["Person"]) == 1
        assert len(data.relationships) == 1
        assert len(data.documents) == 1

    def test_merge(self):
        d1 = NormalizedData(
            entities={"Person": [{"name": "Alice"}]},
            relationships=[{"type": "KNOWS"}],
            documents=[{"title": "Doc1"}],
        )
        d2 = NormalizedData(
            entities={
                "Person": [{"name": "Bob"}],
                "Org": [{"name": "Acme"}],
            },
            relationships=[{"type": "WORKS_FOR"}],
            documents=[{"title": "Doc2"}],
        )
        merged = d1.merge(d2)
        assert len(merged.entities["Person"]) == 2
        assert len(merged.entities["Org"]) == 1
        assert len(merged.relationships) == 2
        assert len(merged.documents) == 2


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestConnectorRegistry:
    def test_all_seven_registered(self):
        assert len(CONNECTOR_REGISTRY) == 7

    def test_expected_connectors(self):
        expected = {"github", "notion", "jira", "slack", "gmail", "gcal", "salesforce"}
        assert set(CONNECTOR_REGISTRY.keys()) == expected

    def test_get_connector(self):
        conn = get_connector("github")
        assert conn.service_name == "GitHub"

    def test_get_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown connector"):
            get_connector("unknown-service")

    def test_list_connectors(self):
        result = list_connectors()
        assert len(result) == 7
        ids = {c["id"] for c in result}
        assert "github" in ids

    def test_all_have_credential_prompts(self):
        for name, cls in CONNECTOR_REGISTRY.items():
            conn = cls()
            prompts = conn.get_credential_prompts()
            assert isinstance(prompts, list)


# ---------------------------------------------------------------------------
# Merge helper
# ---------------------------------------------------------------------------


class TestMergeResults:
    def test_empty_list(self):
        result = merge_connector_results([])
        assert result.entities == {}

    def test_merge_multiple(self):
        r1 = NormalizedData(entities={"A": [{"name": "a"}]})
        r2 = NormalizedData(entities={"B": [{"name": "b"}]})
        r3 = NormalizedData(entities={"A": [{"name": "c"}]})
        merged = merge_connector_results([r1, r2, r3])
        assert len(merged.entities["A"]) == 2
        assert len(merged.entities["B"]) == 1


# ---------------------------------------------------------------------------
# Individual connector tests (mocked external APIs)
# ---------------------------------------------------------------------------


class TestGitHubConnector:
    def test_requires_pygithub(self):
        conn = get_connector("github")
        with patch.dict("sys.modules", {"github": None}):
            with pytest.raises(ImportError):
                conn.authenticate({"token": "fake", "repo": "owner/repo"})

    def test_fetch_returns_normalized_data(self):
        # Mock the GitHub module
        mock_github_module = MagicMock()
        mock_repo = MagicMock()
        mock_repo.full_name = "owner/repo"
        mock_repo.description = "Test repo"
        mock_repo.html_url = "https://github.com/owner/repo"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 10
        mock_repo.organization = None
        mock_repo.get_issues.return_value = []
        mock_repo.get_pulls.return_value = []
        mock_repo.get_commits.return_value = []

        mock_client = MagicMock()
        mock_client.get_repo.return_value = mock_repo
        mock_github_module.Github.return_value = mock_client

        with patch.dict("sys.modules", {"github": mock_github_module}):
            from create_context_graph.connectors.github_connector import GitHubConnector

            conn = GitHubConnector()
            conn.authenticate({"token": "fake", "repo": "owner/repo"})
            result = conn.fetch()

        assert isinstance(result, NormalizedData)
        assert "Repository" in result.entities
        assert len(result.entities["Repository"]) == 1


class TestNotionConnector:
    def test_fetch_returns_normalized_data(self):
        mock_notion_module = MagicMock()
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_notion_module.Client.return_value = mock_client

        with patch.dict("sys.modules", {"notion_client": mock_notion_module}):
            from create_context_graph.connectors.notion_connector import NotionConnector

            conn = NotionConnector()
            conn.authenticate({"token": "fake"})
            result = conn.fetch()

        assert isinstance(result, NormalizedData)


class TestJiraConnector:
    def test_fetch_returns_normalized_data(self):
        mock_atlassian_module = MagicMock()
        mock_jira = MagicMock()
        mock_jira.project.return_value = {"name": "Test Project"}
        mock_jira.jql.return_value = {"issues": []}
        mock_atlassian_module.Jira.return_value = mock_jira

        with patch.dict("sys.modules", {"atlassian": mock_atlassian_module}):
            from create_context_graph.connectors.jira_connector import JiraConnector

            conn = JiraConnector()
            conn.authenticate({
                "url": "https://test.atlassian.net",
                "email": "test@test.com",
                "token": "fake",
                "project": "TEST",
            })
            result = conn.fetch()

        assert isinstance(result, NormalizedData)
        assert "Project" in result.entities


class TestSlackConnector:
    def test_fetch_returns_normalized_data(self):
        mock_slack_module = MagicMock()
        mock_client = MagicMock()
        mock_client.conversations_list.return_value = {"channels": []}
        mock_slack_module.WebClient.return_value = mock_client

        with patch.dict("sys.modules", {"slack_sdk": mock_slack_module}):
            from create_context_graph.connectors.slack_connector import SlackConnector

            conn = SlackConnector()
            conn.authenticate({"token": "xoxb-fake", "channels": "all"})
            result = conn.fetch()

        assert isinstance(result, NormalizedData)


class TestGmailConnector:
    @patch("create_context_graph.connectors.gmail_connector.check_gws_cli", return_value=True)
    @patch("create_context_graph.connectors.gmail_connector.run_gws_command")
    def test_fetch_via_gws(self, mock_gws, mock_check):
        mock_gws.return_value = []

        from create_context_graph.connectors.gmail_connector import GmailConnector

        conn = GmailConnector()
        conn.authenticate({})
        result = conn.fetch()

        assert isinstance(result, NormalizedData)

    @patch("create_context_graph.connectors.gmail_connector.check_gws_cli", return_value=False)
    def test_fallback_needs_credentials(self, mock_check):
        from create_context_graph.connectors.gmail_connector import GmailConnector

        conn = GmailConnector()
        prompts = conn.get_credential_prompts()
        assert len(prompts) == 2  # client_id and client_secret


class TestGCalConnector:
    @patch("create_context_graph.connectors.gcal_connector.check_gws_cli", return_value=True)
    @patch("create_context_graph.connectors.gcal_connector.run_gws_command")
    def test_fetch_via_gws(self, mock_gws, mock_check):
        mock_gws.return_value = []

        from create_context_graph.connectors.gcal_connector import GCalConnector

        conn = GCalConnector()
        conn.authenticate({})
        result = conn.fetch()

        assert isinstance(result, NormalizedData)


class TestSalesforceConnector:
    def test_requires_simple_salesforce(self):
        conn = get_connector("salesforce")
        with patch.dict("sys.modules", {"simple_salesforce": None}):
            with pytest.raises(ImportError):
                conn.authenticate({
                    "username": "test",
                    "password": "test",
                    "security_token": "test",
                    "domain": "login",
                })


# ---------------------------------------------------------------------------
# OAuth helper tests
# ---------------------------------------------------------------------------


class TestOAuthHelpers:
    def test_check_gws_cli(self):
        from create_context_graph.connectors.oauth import check_gws_cli

        # Should return bool regardless of system state
        result = check_gws_cli()
        assert isinstance(result, bool)

    @patch("shutil.which", return_value=None)
    def test_check_gws_cli_not_found(self, mock_which):
        from create_context_graph.connectors.oauth import check_gws_cli

        assert check_gws_cli() is False

    @patch("shutil.which", return_value="/usr/local/bin/gws")
    def test_check_gws_cli_found(self, mock_which):
        from create_context_graph.connectors.oauth import check_gws_cli

        assert check_gws_cli() is True
