import typer
from rich.console import Console
from rich.table import Table
from typing import Annotated

from llm_lib_lag.models import TechVersionGroundTruth
from .ground_truths import GROUND_TRUTHS
from .fetchers import fetch_latest_version_and_date

app = typer.Typer(
    help="LLM Library Lag CLI - Test and validate library version ground truths",
    add_completion=False,
)
console = Console()


@app.command()
def test(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Show detailed test output")
    ] = False,
    fail_fast: Annotated[
        bool, typer.Option("--fail-fast", "-f", help="Stop on first failure")
    ] = False,
) -> None:
    """
    Test ground truth versions against fetched latest versions.

    This command validates that our ground truth data matches the actual latest versions
    from package repositories. It helps ensure our test data stays accurate and catches
    any API or scraping issues.
    """
    table = Table(title="Ground Truth Test Results")
    table.add_column("Library", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Fetched Version", style="blue")
    table.add_column("Ground Truth", style="green")
    table.add_column("Release Date", style="yellow")

    total_ground_truths = len(GROUND_TRUTHS)
    ground_truths_passed = 0
    failures: list[TechVersionGroundTruth] = []

    with console.status("[bold blue]Testing ground truths..."):
        for ground_truth in GROUND_TRUTHS:
            try:
                fetched_latest_version, latest_date = fetch_latest_version_and_date(
                    ground_truth.tech
                )

                if (
                    fetched_latest_version == ground_truth.version
                    and latest_date == ground_truth.release_date
                ):
                    ground_truths_passed += 1
                    table.add_row(
                        str(ground_truth.tech),
                        "✅ PASS",
                        fetched_latest_version,
                        ground_truth.version,
                        str(latest_date),
                    )
                else:
                    failures.append(ground_truth)
                    table.add_row(
                        str(ground_truth.tech),
                        "❌ FAIL",
                        f"{fetched_latest_version} ({latest_date})",
                        f"{ground_truth.version} ({ground_truth.release_date})",
                        "Mismatch",
                        style="red",
                    )
                    if fail_fast:
                        break

            except Exception as e:
                failures.append(ground_truth)
                table.add_row(
                    str(ground_truth.tech),
                    "❌ ERROR",
                    str(e),
                    ground_truth.version,
                    str(ground_truth.release_date),
                    style="red",
                )
                if fail_fast:
                    break

    if verbose or failures:
        console.print(table)

    if ground_truths_passed == total_ground_truths:
        console.print(
            f"\n[green]All {total_ground_truths} ground truths passed! 🎉[/green]"
        )
    else:
        console.print(
            f"\n[red]{ground_truths_passed}/{total_ground_truths} ground truths passed[/red]"
        )
        raise typer.Exit(code=1)


def main() -> None:
    app()
