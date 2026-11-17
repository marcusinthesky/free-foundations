"""The small publication CLI rejects undeclared experiment overrides."""

from pathlib import Path

import pytest
import yaml
from typer.main import get_command
from typer.testing import CliRunner

from free_foundations import cli
from free_foundations.panel import run as panel_run

RUNNER = CliRunner()
PIPELINE = Path(__file__).parents[3] / "dvc.yaml"


def commands() -> list[tuple[str, str]]:
    """Every registered group/command pair."""
    groups = get_command(cli.app).commands  # type: ignore[attr-defined]
    return [(group, name) for group, item in groups.items() for name in item.commands]


@pytest.mark.parametrize(("group", "name"), commands())
def test_every_command_resolves(group: str, name: str) -> None:
    result = RUNNER.invoke(cli.app, [group, name, "--help"])
    assert result.exit_code == 0, result.output


def test_panel_run_uses_the_fixed_study(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []
    monkeypatch.setattr(panel_run, "main", lambda: calls.append("study"))
    result = RUNNER.invoke(cli.app, ["panel", "run"])
    assert result.exit_code == 0, result.output
    assert calls == ["study"]


@pytest.mark.parametrize("option", ["--design", "--model"])
def test_arbitrary_overrides_are_rejected_before_work(
    option: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse() -> None:
        pytest.fail("ran an undeclared experiment")

    monkeypatch.setattr(panel_run, "main", refuse)
    result = RUNNER.invoke(cli.app, ["panel", "run", option, "other"])
    assert result.exit_code == 2
    assert "No such option" in result.output


def test_only_retained_research_commands_are_exposed() -> None:
    assert set(commands()) == {
        ("universe", "run"),
        ("models", "checkpoints"),
        ("fernandez", "run"),
        ("panel", "prepare"),
        ("panel", "encode"),
        ("panel", "run"),
        ("panel", "report"),
        ("study", "acquire"),
        ("study", "link"),
        ("study", "freeze"),
        ("study", "prepare"),
        ("study", "encode"),
        ("study", "run"),
        ("study", "replicate"),
        ("study", "report"),
    }


def test_every_stage_runs_a_registered_command() -> None:
    pipeline = yaml.safe_load(PIPELINE.read_text())
    variables = {name: value for item in pipeline["vars"] for name, value in item.items()}
    registered = {f"free-foundations {group} {name}" for group, name in commands()}
    for stage in pipeline["stages"].values():
        command = stage["cmd"]
        if stage.get("frozen"):
            assert command == "false"
            continue
        for name, value in variables.items():
            command = command.replace(f"${{{name}}}", value)
        words = command.split()
        start = words.index("free-foundations")
        assert " ".join(words[start : start + 3]) in registered, command


def test_source_acquisition_defaults_to_recovery_staging(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def record(*_args: object, **kwargs: object) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(cli.study_run, "acquire", record)
    result = RUNNER.invoke(cli.app, ["study", "acquire", "--offline", "--metadata-only"])
    assert result.exit_code == 0, result.output
    assert calls[0]["output"] == Path("research/crsp-study/recovery")
    assert calls[0]["offline"] is True
    assert calls[0]["metadata_only"] is True


def test_freeze_cli_forwards_staging_and_canonical_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def record(**kwargs: object) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(cli.study_run, "freeze", record)
    result = RUNNER.invoke(
        cli.app, ["study", "freeze", "--staging", "staged", "--output", "frozen"]
    )
    assert result.exit_code == 0, result.output
    assert calls == [{"staging": Path("staged"), "output": Path("frozen")}]
