#!/usr/bin/env python

import click
import os
from pathlib import Path


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.group()
@click.option(
    "-f",
    "--expansion-file",
    type=click.Path(path_type=Path),
    default=lambda: Path(os.environ.get("HOME", "/")) / Path(".expanserc"),
)
@click.pass_context
def cli(ctx, expansion_file):
    ctx.ensure_object(dict)

    ctx.obj["EXPANSION_FILE"] = expansion_file


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.pass_context
def add(ctx, name):
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
def delete(ctx, name):
    "Remove expansion"
    pass


@cli.command()
@click.pass_context
def list(ctx):
    "List expansions"
    pass


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.pass_context
def show(ctx, name):
    "Show expansion"
    pass


if __name__ == "__main__":
    cli(obj={})
