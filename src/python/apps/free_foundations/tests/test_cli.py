"""The CLI exposes exactly the layered pipeline stages that DVC runs."""

from pathlib import Path

import pytest
import yaml
from typer.main import get_command
from typer.testing import CliRunner

from free_foundations import cli
from free_foundations.stages import raw

RUNNER = CliRunner()
PIPELINE = (
    next(p for p in Path(__file__).resolve().parents if (p / "dvc.yaml").is_file()) / "dvc.yaml"
)


def commands() -> list[tuple[str, str, str]]:
    """Every registered stages/layer/command triple."""
    groups = get_command(cli.app).commands  # type: ignore[attr-defined]
    return [
        (group, layer, name)
        for group, item in groups.items()
        for layer, sub in item.commands.items()
        for name in sub.commands
    ]


@pytest.mark.component
@pytest.mark.parametrize(("group", "layer", "name"), commands())
def test_every_command_resolves(group: str, layer: str, name: str) -> None:
    # Act
    result = RUNNER.invoke(cli.app, [group, layer, name, "--help"])

    # Assert
    assert result.exit_code == 0, result.output


@pytest.mark.unit
def test_only_layered_pipeline_commands_are_exposed() -> None:
    # Act / Assert
    assert set(commands()) == {
        ("stages", "raw", "acquire"),
        ("stages", "raw", "link"),
        ("stages", "raw", "freeze"),
        ("stages", "raw", "checkpoints"),
        ("stages", "processed", "prepare"),
        ("stages", "processed", "encode"),
        ("stages", "research", "replicate"),
        ("stages", "research", "comovement"),
        ("stages", "research", "alignment"),
        ("stages", "research", "publish"),
    }


@pytest.mark.unit
def test_every_stage_runs_a_registered_command() -> None:
    # Arrange
    pipeline = yaml.safe_load(PIPELINE.read_text())
    variables = {name: value for item in pipeline["vars"] for name, value in item.items()}
    registered = {f"free-foundations {' '.join(triple)}" for triple in commands()}

    # Act / Assert
    for stage in pipeline["stages"].values():
        command = stage["cmd"]
        if stage.get("frozen"):
            assert command == "false"
            continue
        for name, value in variables.items():
            command = command.replace(f"${{{name}}}", value)
        words = command.split()
        if "semflow" in words:
            assert words[words.index("semflow") + 1 :] == ["refresh", "--apply"], command
            continue
        # `--package free-foundations` names the project; the executable is the last mention.
        start = len(words) - 1 - words[::-1].index("free-foundations")
        assert " ".join(words[start : start + 4]) in registered, command


@pytest.mark.component
def test_acquisition_writes_staging_and_forwards_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    calls = []

    def record(*_args: object, **kwargs: object) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(raw.run, "acquire", record)

    # Act
    result = RUNNER.invoke(
        cli.app,
        [
            "stages",
            "raw",
            "acquire",
            "--crsp-csv",
            "extract.csv",
            "--extraction-script",
            "extract.py",
            "--offline",
            "--metadata-only",
        ],
    )

    # Assert
    assert result.exit_code == 0, result.output
    assert calls[0]["staging"] == Path("data/staging/crsp-sec")
    assert calls[0]["canonical"] == Path("data/raw/crsp-sec")
    assert calls[0]["offline"] is True
    assert calls[0]["metadata_only"] is True


@pytest.mark.component
def test_freeze_forwards_staging_and_canonical_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    calls = []

    def record(**kwargs: object) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(raw.run, "freeze", record)

    # Act
    result = RUNNER.invoke(
        cli.app,
        ["stages", "raw", "freeze", "--staging", "staged", "--canonical", "frozen"],
    )

    # Assert
    assert result.exit_code == 0, result.output
    assert calls == [
        {"staging": Path("staged"), "canonical": Path("frozen"), "params": Path("params.yaml")}
    ]
