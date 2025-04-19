#!/usr/bin/env python3

import sys
from pathlib import Path

import click
from click.termui import confirm

from .core import get_expfile, load_expansions, save_expansions, ensure_expfile


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    expfile = get_expfile()
    ctx.obj["EXPANSION_FILE"] = expfile
    if not ensure_expfile(expfile):
        click.echo(f"Could not access expansion file {expfile}", err=True)
        ctx.abort()


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.pass_context
def edit(ctx, name: str) -> None:
    "Edit expansion"
    expfile = ctx.obj["EXPANSION_FILE"]
    exps = load_expansions(expfile)
    if not name in exps["expansions"]:
        click.echo(f"No such expansion: {name}, creating new one")
        expansion = ""
    else:
        expansion = exps["expansions"][name]
    expansion = click.edit(expansion)
    exps["expansions"][name] = expansion
    if not save_expansions(expfile, exps):
        click.echo(f"Could not write to {expfile}.", err=True)
        ctx.abort()


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.option("-e", "--expansion")
@click.pass_context
def add(ctx, name: str, expansion: str) -> None:
    "Add expansion"
    expfile = ctx.obj["EXPANSION_FILE"]
    exps = load_expansions(expfile)
    if name in exps["expansions"] and not click.confirm(f"Expansion {name} already exists. Overwrite?"):
        ctx.abort()
    if not expansion:
        click.echo("Enter expansion. Terminate with ctrl-D:")
        expansion = "".join(sys.stdin.readlines()).strip()
    exps["expansions"][name] = expansion
    if not save_expansions(expfile, exps):
        click.echo(f"Could not write to {expfile}.", err=True)
        ctx.abort()


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.option(
    "--yes",
    is_flag=True,
    callback=lambda ctx, param, value: not value and ctx.abort(),
    expose_value=False,
    prompt="Really delete expansion?",
)
@click.pass_context
def delete(ctx, name: str) -> None:
    "Remove expansion"
    expfile = ctx.obj["EXPANSION_FILE"]
    exps = load_expansions(expfile)
    if not name in exps["expansions"]:
        click.echo(f"No such expansion: {name}", err=True)
        ctx.abort()
    del exps["expansions"][name]
    if not save_expansions(expfile, exps):
        click.echo(f"Could not write to {expfile}.", err=True)
        ctx.abort()


@cli.command()
@click.pass_context
def list(ctx) -> None:
    "List expansions"
    exps = load_expansions(ctx.obj["EXPANSION_FILE"])
    for z in exps["expansions"]:
        print(z)


@cli.command()
@click.option("-n", "--name", prompt=True)
@click.pass_context
def show(ctx, name: str) -> None:
    "Show expansion"
    exps = load_expansions(ctx.obj["EXPANSION_FILE"])
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
    exps = load_expansions(ctx.obj["EXPANSION_FILE"])
    for name in names:
        if name in exps["expansions"]:
            print(exps["expansions"].get(name))


@cli.command()
@click.pass_context
def dump(ctx) -> None:
    "Dump expansion file"
    exps = load_expansions(ctx.obj["EXPANSION_FILE"])
    for name, expansion in exps["expansions"].items():
        expansion = expansion.replace("\n", "↵")
        print(f"{name}\n{expansion}")


def main():
    cli(obj={})
