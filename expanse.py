#!/usr/bin/env python

from json.decoder import JSONDecodeError
import click
import json
import os
from pathlib import Path

from click.termui import confirm


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def ensure_expfile(expfile: Path) -> bool:
    # If the file exists, load it and check (roughly) for the correct format
    if expfile.exists():
        try:
            with expfile.open() as f:
                json.load(f)["expansions"]
        except (JSONDecodeError, KeyError):
            click.echo(f"Expansion file {expfile} is an invalid format", err=True)
            return False
        return True

    # Otherwise create an empty file
    if not click.confirm("Expansion file does not exist. Create?"):
        return False
    try:
        with expfile.open("w") as f:
            json.dump({"expansions": {}}, f)
    except OSError:
        click.echo(f"Could not write to {expfile}.", err=True)
        return False
    return True


@click.group()
@click.option(
    "-f",
    "--expansion-file",
    type=click.Path(path_type=Path),
    default=lambda: Path(os.environ.get("HOME", "/")) / Path(".expanserc"),
)
@click.pass_context
def cli(ctx, expansion_file: Path) -> None:
    ctx.ensure_object(dict)
    ctx.obj["EXPANSION_FILE"] = expansion_file
    if not ensure_expfile(expansion_file):
        ctx.abort()


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.pass_context
def add(ctx, name: str) -> None:
    "Add expansion"
    pass


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.option(
    "--yes",
    is_flag=True,
    callback=abort_if_false,
    expose_value=False,
    prompt="Really delete expansion?",
)
@click.pass_context
def delete(ctx, name: str) -> None:
    "Remove expansion"
    pass


@cli.command()
@click.pass_context
def list(ctx) -> None:
    "List expansions"
    with ctx.obj["EXPANSION_FILE"].open() as f:
        exps = json.load(f)
    for z in exps["expansions"]:
        print(z)


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.pass_context
def show(ctx, name: str) -> None:
    "Show expansion"
    pass


if __name__ == "__main__":
    cli(obj={})
