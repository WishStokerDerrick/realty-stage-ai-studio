"""CLI entry point. Thin — parses args, wires services, calls one pipeline."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from realty_stage_ai.bootstrap.wiring import build_container
from realty_stage_ai.config.settings import load_settings
from realty_stage_ai.models.staging_request import StagingRequest
from realty_stage_ai.pipelines.stage_listing import StageListingPipeline

app = typer.Typer(add_completion=False, help="AI virtual staging for real-estate photos.")
console = Console()


@app.command()
def stage(
    photo: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    preset: str = typer.Option("modern_warm", "--preset", "-p"),
    room: str = typer.Option("auto", "--room", "-r"),
    out: Path = typer.Option(Path("staging_out"), "--out", "-o"),
    seed: int = typer.Option(6767, "--seed"),
) -> None:
    """Stage a single listing photo with the given preset."""
    settings = load_settings()
    container = build_container(settings)
    request = StagingRequest(
        source=photo,
        preset=preset,
        room=room,
        output_dir=out,
        seed=seed,
    )
    pipeline = StageListingPipeline(container=container)
    result = pipeline.run(request)
    console.print(f"[bold green]staged[/] {result.output_path} ({result.elapsed_ms} ms)")


def main() -> None:
    app()


if __name__ == "__main__":
    main()