#!/usr/bin/env python3

import json
import os
import sys
from json.decoder import JSONDecodeError
from pathlib import Path, PosixPath

import click
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


# we have to specify PosixPath explicitly because things break in the test suite
# otherwise due to https://bugs.python.org/issue24132
@click.group()
@click.option(
    "-f",
    "--expansion-file",
    type=click.Path(path_type=PosixPath),
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
def edit(ctx, name: str) -> None:
    "Edit expansion"
    expfile = ctx.obj["EXPANSION_FILE"]
    with expfile.open() as f:
        exps = json.load(f)
    if not name in exps["expansions"]:
        click.echo(f"No such expansion: {name}, creating new one")
        expansion = ""
    else:
        expansion = exps["expansions"][name]
    expansion = click.edit(expansion)
    exps["expansions"][name] = expansion
    try:
        with expfile.open("w") as f:
            json.dump(exps, f)
    except OSError:
        click.echo(f"Could not write to {expfile}.", err=True)
        ctx.abort()


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.option("-e", "--expansion")
@click.pass_context
def add(ctx, name: str, expansion: str) -> None:
    "Add expansion"
    expfile = ctx.obj["EXPANSION_FILE"]
    with expfile.open() as f:
        exps = json.load(f)
    if name in exps["expansions"] and not click.confirm(
        f"Expansion {name} already exists. Overwrite?"
    ):
        ctx.abort()
    if not expansion:
        click.echo("Enter expansion. Terminate with ctrl-D:")
        expansion = "".join(sys.stdin.readlines()).strip()
    exps["expansions"][name] = expansion
    try:
        with expfile.open("w") as f:
            json.dump(exps, f)
    except OSError:
        click.echo(f"Could not write to {expfile}.", err=True)
        ctx.abort()


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
    expfile = ctx.obj["EXPANSION_FILE"]
    with expfile.open() as f:
        exps = json.load(f)
    if not name in exps["expansions"]:
        click.echo(f"No such expansion: {name}", err=True)
        ctx.abort()
    del exps["expansions"][name]
    try:
        with expfile.open("w") as f:
            json.dump(exps, f)
    except OSError:
        click.echo(f"Could not write to {expfile}.", err=True)
        ctx.abort()


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
    with ctx.obj["EXPANSION_FILE"].open() as f:
        exps = json.load(f)
    if not name in exps["expansions"]:
        click.echo(f"No such expansion: {name}", err=True)
        ctx.abort()
    click.echo(click.style(f"'{name}'", fg="green"))
    print(exps["expansions"][name])


@cli.command()
@click.pass_context
@click.argument("names", nargs=-1)
def get(ctx, names: str) -> None:
    "Get expansion contents"
    with ctx.obj["EXPANSION_FILE"].open() as f:
        exps = json.load(f)
    for name in names:
        if name in exps["expansions"]:
            print(exps["expansions"].get(name))


@cli.command()
@click.pass_context
def dump(ctx) -> None:
    "Dump expansion file"
    with ctx.obj["EXPANSION_FILE"].open() as f:
        exps = json.load(f)
    for name, expansion in exps["expansions"].items():
        expansion = expansion.replace("\n", "↵")
        print(f"{name}\n{expansion}")


if __name__ == "__main__":
    cli(obj={})
