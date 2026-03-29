# Copyright 2026 Neo4j Labs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for the CLI module."""

import json

import pytest
from click.testing import CliRunner

from create_context_graph.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestListDomains:
    def test_list_domains(self, runner):
        result = runner.invoke(main, ["--list-domains"])
        assert result.exit_code == 0
        assert "financial-services" in result.output
        assert "healthcare" in result.output
        assert "software-engineering" in result.output

    def test_list_shows_22_domains(self, runner):
        result = runner.invoke(main, ["--list-domains"])
        assert result.exit_code == 0
        # Count non-empty lines that look like domain entries
        lines = [line for line in result.output.strip().split("\n") if line.strip() and not line.startswith("Available")]
        assert len(lines) >= 22


class TestVersion:
    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output


class TestScaffoldGeneration:
    def test_basic_scaffold(self, runner, tmp_path):
        out = tmp_path / "my-app"
        result = runner.invoke(main, [
            "my-app",
            "--domain", "financial-services",
            "--framework", "pydanticai",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output
        assert (out / "backend" / "app" / "main.py").exists()
        assert (out / "frontend" / "package.json").exists()

    def test_scaffold_with_demo_data(self, runner, tmp_path):
        out = tmp_path / "my-app"
        result = runner.invoke(main, [
            "my-app",
            "--domain", "healthcare",
            "--framework", "claude-agent-sdk",
            "--demo-data",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output
        fixture = out / "data" / "fixtures.json"
        assert fixture.exists()
        data = json.loads(fixture.read_text())
        assert len(data["entities"]) > 0

    def test_invalid_domain(self, runner, tmp_path):
        out = tmp_path / "my-app"
        result = runner.invoke(main, [
            "my-app",
            "--domain", "nonexistent-domain",
            "--framework", "pydanticai",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 1

    def test_existing_nonempty_dir_fails(self, runner, tmp_path):
        out = tmp_path / "my-app"
        out.mkdir()
        (out / "existing-file.txt").write_text("hello")

        result = runner.invoke(main, [
            "my-app",
            "--domain", "financial-services",
            "--framework", "pydanticai",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 1
        assert "not empty" in result.output


class TestNeo4jAuraEnv:
    """Test --neo4j-aura-env CLI flag."""

    def test_aura_env_flag(self, runner, tmp_path):
        # Create a fake Aura .env file
        aura_env = tmp_path / "aura.env"
        aura_env.write_text(
            'NEO4J_URI=neo4j+s://abc123.databases.neo4j.io\n'
            'NEO4J_USERNAME=neo4j\n'
            'NEO4J_PASSWORD=super-secret\n'
        )
        out = tmp_path / "aura-app"
        result = runner.invoke(main, [
            "aura-app",
            "--domain", "financial-services",
            "--framework", "pydanticai",
            "--neo4j-aura-env", str(aura_env),
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output

        # Verify credentials were parsed into .env
        env = (out / ".env").read_text()
        assert "neo4j+s://abc123.databases.neo4j.io" in env
        assert "super-secret" in env

        # Verify no docker-compose for aura type
        assert not (out / "docker-compose.yml").exists()

    def test_neo4j_local_flag(self, runner, tmp_path):
        out = tmp_path / "local-app"
        result = runner.invoke(main, [
            "local-app",
            "--domain", "financial-services",
            "--framework", "pydanticai",
            "--neo4j-local",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output

        makefile = (out / "Makefile").read_text()
        assert "neo4j-start:" in makefile
        assert not (out / "docker-compose.yml").exists()

    def test_maf_alias_still_works(self, runner, tmp_path):
        """Verify deprecated 'maf' alias resolves to anthropic-tools."""
        out = tmp_path / "maf-app"
        result = runner.invoke(main, [
            "maf-app",
            "--domain", "financial-services",
            "--framework", "maf",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output
        agent = (out / "backend" / "app" / "agent.py").read_text()
        assert "Anthropic Tools" in agent


class TestMultipleDomainScaffolds:
    """Integration test: scaffold generation works for multiple domains."""

    @pytest.mark.parametrize("domain_id,framework", [
        ("financial-services", "pydanticai"),
        ("healthcare", "claude-agent-sdk"),
        ("software-engineering", "openai-agents"),
        ("wildlife-management", "langgraph"),
        ("gaming", "crewai"),
        ("manufacturing", "strands"),
        ("digital-twin", "google-adk"),
        ("retail-ecommerce", "anthropic-tools"),
    ])
    def test_domain_framework_combo(self, runner, tmp_path, domain_id, framework):
        out = tmp_path / f"test-{domain_id}"
        result = runner.invoke(main, [
            f"test-{domain_id}",
            "--domain", domain_id,
            "--framework", framework,
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, f"{domain_id}/{framework} failed: {result.output}"

        # Check key files
        assert (out / "backend" / "app" / "agent.py").exists()
        assert (out / "frontend" / "lib" / "config.ts").exists()
        assert (out / "cypher" / "schema.cypher").exists()
        assert (out / "data" / "fixtures.json").exists()

        # Verify agent template matches framework
        agent = (out / "backend" / "app" / "agent.py").read_text()
        framework_markers = {
            "pydanticai": "PydanticAI",
            "claude-agent-sdk": "Claude Agent SDK",
            "openai-agents": "OpenAI Agents SDK",
            "langgraph": "LangGraph",
            "crewai": "CrewAI",
            "strands": "Strands",
            "google-adk": "Google ADK",
            "anthropic-tools": "Anthropic Tools",
        }
        marker = framework_markers.get(framework)
        if marker:
            assert marker in agent, f"Agent file missing '{marker}' for framework {framework}"


class TestCLIValidation:
    """Tests for v0.4.0 CLI improvements."""

    def test_dry_run_no_files_created(self, runner, tmp_path):
        out = tmp_path / "dry-run-test"
        result = runner.invoke(main, [
            "dry-run-test",
            "--domain", "healthcare",
            "--framework", "pydanticai",
            "--output-dir", str(out),
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "healthcare" in result.output
        assert not out.exists()

    def test_verbose_flag_accepted(self, runner, tmp_path):
        out = tmp_path / "verbose-test"
        result = runner.invoke(main, [
            "verbose-test",
            "--domain", "healthcare",
            "--framework", "pydanticai",
            "--output-dir", str(out),
            "--verbose",
        ])
        assert result.exit_code == 0


class TestV060CLIFlags:
    """Tests for v0.6.0 CLI additions."""

    def test_demo_flag_accepted_dry_run(self, runner, tmp_path):
        """--demo flag should be accepted and expand to --reset-database --demo-data --ingest."""
        out = tmp_path / "demo-test"
        result = runner.invoke(main, [
            "demo-test",
            "--domain", "healthcare",
            "--framework", "pydanticai",
            "--output-dir", str(out),
            "--demo",
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "Dry run" in result.output

    def test_no_project_name_auto_generates_slug(self, runner, tmp_path):
        """When PROJECT_NAME is omitted but --domain and --framework are provided, auto-generate slug."""
        out = tmp_path / "auto-slug"
        result = runner.invoke(main, [
            "--domain", "healthcare",
            "--framework", "pydanticai",
            "--output-dir", str(out),
            "--dry-run",
        ])
        assert result.exit_code == 0, result.output
        assert "Dry run" in result.output
        assert "healthcare-pydanticai-app" in result.output

    def test_google_api_key_flag(self, runner, tmp_path):
        """--google-api-key should flow through to rendered .env."""
        out = tmp_path / "gkey-test"
        result = runner.invoke(main, [
            "gkey-test",
            "--domain", "healthcare",
            "--framework", "google-adk",
            "--google-api-key", "test-gkey-123",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output
        env_content = (out / ".env").read_text()
        assert "GOOGLE_API_KEY=test-gkey-123" in env_content

    def test_google_adk_warning_without_key(self, runner, tmp_path):
        """google-adk without --google-api-key should print a warning."""
        out = tmp_path / "adk-warn"
        result = runner.invoke(main, [
            "adk-warn",
            "--domain", "healthcare",
            "--framework", "google-adk",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output
        assert "Warning" in result.output
        assert "GOOGLE_API_KEY" in result.output

    def test_openai_api_key_flag(self, runner, tmp_path):
        """--openai-api-key should flow through to rendered .env."""
        out = tmp_path / "okey-test"
        result = runner.invoke(main, [
            "okey-test",
            "--domain", "healthcare",
            "--framework", "pydanticai",
            "--openai-api-key", "sk-test-openai",
            "--output-dir", str(out),
        ])
        assert result.exit_code == 0, result.output
        env_content = (out / ".env").read_text()
        assert "OPENAI_API_KEY=sk-test-openai" in env_content
