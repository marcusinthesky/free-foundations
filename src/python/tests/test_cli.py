"""The command line forwards to the study functions that DVC stages fingerprint."""

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
    """Every (group, command) pair the application registers."""
    groups = get_command(cli.app).commands  # type: ignore[attr-defined]
    return [(group, name) for group, item in groups.items() for name in item.commands]


@pytest.mark.parametrize(("group", "name"), commands())
def test_every_command_resolves(group: str, name: str) -> None:
    result = RUNNER.invoke(cli.app, [group, name, "--help"])
    assert result.exit_code == 0, result.output


def test_panel_run_forwards_each_design_and_model(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], list[str] | None]] = []

    def record(designs: list[str], models: list[str] | None) -> None:
        calls.append((designs, models))

    monkeypatch.setattr(panel_run, "main", record)
    arguments = ["panel", "run", "--design", "three", "--design", "four", "--model", "tabfm"]
    result = RUNNER.invoke(cli.app, arguments)
    assert result.exit_code == 0, result.output
    assert calls == [(["three", "four"], ["tabfm"])]


def test_undeclared_designs_are_rejected_before_any_work(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*_: object) -> None:
        pytest.fail("ran an undeclared design")

    monkeypatch.setattr(panel_run, "main", refuse)
    result = RUNNER.invoke(cli.app, ["panel", "run", "--design", "five"])
    assert result.exit_code == 2
    assert "five not in" in result.output


def test_every_stage_runs_a_registered_command() -> None:
    """A renamed command must not leave a DVC stage pointing at nothing."""
    pipeline = yaml.safe_load(PIPELINE.read_text())
    variables = {name: value for item in pipeline["vars"] for name, value in item.items()}
    registered = {f"free-foundations {group} {name}" for group, name in commands()}
    for stage_name, stage in pipeline["stages"].items():
        command = stage["cmd"]
        if stage_name == "market_metadata":
            assert stage["frozen"] is True
            assert command == "false"
            continue
        for name, value in variables.items():
            command = command.replace(f"${{{name}}}", value)
        words = command.split()
        start = words.index("free-foundations")
        assert " ".join(words[start : start + 3]) in registered, command
