"""Command line entry point for Foley."""

from collections.abc import Callable
import json
from pathlib import Path
from typing import Annotated, Any

from pydantic import ValidationError
import typer

# Typer 0.27 vendors Click, so a command that overrides Click's own hooks has to speak the vendored types.
from typer._click import Context, Parameter
from typer.core import TyperCommand, TyperOption
from typer.models import CommandFunctionType

from foley import lib
from foley.scene import Scene
from foley.schemas import DEFAULT_PROVIDER, FoleyError, ReasoningEffort


class CapabilityCommand(TyperCommand):
    """Every capability answers `-h` with the generated summary and `--help` with its skill from the library."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["add_help_option"] = False
        super().__init__(*args, **kwargs)

    def get_params(self, ctx: Context) -> list[Parameter]:
        def short(ctx: Context, param: Parameter, value: bool) -> None:
            if value and not ctx.resilient_parsing:
                typer.echo(ctx.get_help())
                ctx.exit()

        def capability_skill(ctx: Context, param: Parameter, value: bool) -> None:
            if value and not ctx.resilient_parsing:
                typer.echo(lib.skill(self.name))
                ctx.exit()

        return [
            *super().get_params(ctx),
            TyperOption(
                param_decls=["-h"],
                is_flag=True,
                is_eager=True,
                expose_value=False,
                callback=short,
                help="Terse summary of this capability.",
            ),
            TyperOption(
                param_decls=["--help"],
                is_flag=True,
                is_eager=True,
                expose_value=False,
                callback=capability_skill,
                help="This capability's skill, for an agent about to call it.",
            ),
        ]


class SmartToolTyper(typer.Typer):
    """A Typer whose commands are CapabilityCommand by default, so a capability added later inherits the help split."""

    def command(
        self, *args: Any, cls: type[TyperCommand] = CapabilityCommand, **kwargs: Any
    ) -> Callable[[CommandFunctionType], CommandFunctionType]:
        return super().command(*args, cls=cls, **kwargs)


app = SmartToolTyper(
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    # `-h` is the terse summary and `--help` is the skill, at both scopes. On the root, the callback's parameter
    # claims `--help` and Click drops a help option name a parameter already took, which leaves the generated
    # summary on `-h`; on a capability, CapabilityCommand splits the two itself.
    context_settings={"help_option_names": ["-h", "--help"]},
)


def _print_skill(value: bool) -> None:
    """Answer the root `--help` with the skill the library composes, leaving `-h` to Typer."""
    if value:
        typer.echo(lib.skill())
        raise typer.Exit()


@app.callback()
def cli(
    help: Annotated[
        bool,
        typer.Option(
            "--help", is_eager=True, callback=_print_skill, help="This tool's skill, for an agent driving it."
        ),
    ] = False,
) -> None:
    """Design, audition, revise, and export production sound effects with Csound and Amplifier Agent"""


@app.command()
def manifest() -> None:
    """Print the tool's manifest as JSON. Deterministic."""
    typer.echo(lib.load_manifest().model_dump_json(indent=2))


def emit(value: Any) -> None:
    typer.echo(json.dumps(value, indent=2, ensure_ascii=True))


@app.command()
def create(
    brief: str,
    store: Path | None = None,
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
    duration: float = 2,
    channels: int = 2,
    seed: int = 1,
    loop: bool = False,
    reasoning_effort: ReasoningEffort = "medium",
    timeout: int = 300,
) -> None:
    """Design and render a natural-language brief. Model-backed."""
    emit(lib.create(brief, store, provider, model, duration, channels, seed, loop, reasoning_effort, timeout))


@app.command()
def revise(
    revision: str,
    changes: str,
    store: Path | None = None,
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
    duration: float | None = None,
    reasoning_effort: ReasoningEffort = "medium",
    timeout: int = 300,
) -> None:
    """Render a changed child, preserving the original. Model-backed."""
    emit(lib.revise(revision, changes, store, provider, model, duration, reasoning_effort, timeout))


@app.command()
def recipe(
    name: str = "wood-impact", duration: float = 2, seed: int = 1, channels: int = 2, loop: bool = False
) -> None:
    """Print a deterministic scene JSON to redirect into a file."""
    emit(lib.recipe(name, duration, seed, channels, loop).model_dump())


@app.command()
def render(scene_file: Path, store: Path | None = None, brief: str = "") -> None:
    """Render a validated scene JSON file. Deterministic."""
    if scene_file.stat().st_size > 1_000_000:
        raise FoleyError("Scene exceeds 1 MB; use a bounded scene with up to 32 layers.")
    emit(lib.render(Scene.model_validate_json(scene_file.read_text()), store, brief))


@app.command()
def variants(revision: str, seeds: Annotated[list[int], typer.Option("--seed")], store: Path | None = None) -> None:
    """Render up to eight seeded child revisions."""
    emit(lib.variants(revision, seeds, store))


@app.command(name="list")
def list_sounds(store: Path | None = None) -> None:
    """List and verify retained sounds."""
    emit(lib.list_sounds(store))


@app.command()
def inspect(revision: str, store: Path | None = None) -> None:
    """Read an exact retained revision and verify its hashes."""
    emit(lib.inspect(revision, store))


@app.command()
def audition(
    revisions: Annotated[list[str], typer.Argument()],
    destination: Annotated[Path, typer.Option("--destination")],
    store: Path | None = None,
) -> None:
    """Write an offline HTML listening and comparison surface."""
    emit(lib.audition(revisions, destination, store))


@app.command()
def export(
    revision: str,
    destination: Path,
    bundle: bool = False,
    store: Path | None = None,
) -> None:
    """Export a WAV or deterministic audit bundle without replacing files."""
    emit(lib.export(revision, destination, bundle, store))


@app.command()
def doctor(providers: bool = False) -> None:
    """Check installation and optional provider credentials without generation."""
    emit(lib.doctor(providers))


@app.command()
def models(provider: str = DEFAULT_PROVIDER) -> None:
    """Discover model IDs without generating content; may query provider catalogs."""
    emit(lib.models(provider))


def main() -> int:
    try:
        app()
    except FoleyError as error:
        typer.echo(error, err=True)
        return 1
    except ValidationError as error:
        fields = ", ".join(".".join(map(str, item["loc"])) for item in error.errors())
        typer.echo(
            f"Invalid scene/options at {fields}. See command --help and scene schema; no revision published.", err=True
        )
        return 2
    except (OSError, ValueError):
        typer.echo("Invalid or inaccessible input/output. Check paths, JSON and command --help.", err=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
