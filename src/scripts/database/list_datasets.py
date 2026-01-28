#!/usr/bin/env python3
"""CLI for listing datasets in SQLite database."""

from typing import Annotated, Optional

import typer

app = typer.Typer(add_completion=False)


@app.command()
def main(
    tags: Annotated[
        Optional[list[str]],
        typer.Option("--tag", help="Filter by tag (can be specified multiple times)"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show more details"),
    ] = False,
) -> None:
    """List datasets stored in SQLite database."""
    from core.shared.persistence import get_unit_of_work

    with get_unit_of_work() as uow:
        # Get datasets
        if tags:
            # Filter by all specified tags
            datasets = None
            for tag_name in tags:
                tag_datasets = set(d.name for d in uow.datasets.list_by_tag(tag_name))
                datasets = tag_datasets if datasets is None else datasets & tag_datasets
            # Fetch full objects
            datasets_list = [uow.datasets.get_by_name(name) for name in (datasets or [])]
            datasets_list = [d for d in datasets_list if d is not None]
        else:
            datasets_list = uow.datasets.list_all()

        if not datasets_list:
            print("No datasets found.")
            return

        # Print header
        print(f"{'NAME':<30} {'TYPE':<20} {'TAGS':<25} {'CREATED':<20}")
        print("-" * 95)

        for ds in datasets_list:
            # Get data type from first data record
            data_types = set()
            for dr in ds.data_records:
                data_types.add(dr.data_type)
            type_str = ", ".join(sorted(data_types)) if data_types else "-"

            # Get tags
            tag_str = ", ".join(t.name for t in ds.tags) if ds.tags else "-"
            if len(tag_str) > 23:
                tag_str = tag_str[:20] + "..."

            # Format created time
            created_str = ds.created_at.strftime("%Y-%m-%d %H:%M") if ds.created_at else "-"

            print(f"{ds.name:<30} {type_str:<20} {tag_str:<25} {created_str:<20}")

            if verbose:
                print(f"    Source: {ds.source_meta.get('origin', '-')}")
                print(f"    Params: {ds.parameters}")
                print(f"    Records: {len(ds.data_records)}")
                print()

        print(f"\nTotal: {len(datasets_list)} dataset(s)")


if __name__ == "__main__":
    app()
