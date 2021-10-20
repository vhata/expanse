#!/usr/bin/env python

import click


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.group()
def cli():
    pass


@cli.command()
@click.option("-n", "--name", prompt=True)
def add(name):
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
def delete(name):
    "Remove expansion"
    pass


@cli.command()
def list():
    "List expansions"
    pass


@cli.command()
@click.option("-n", "--name", prompt=True)
def show(name):
    "Show expansion"
    pass


if __name__ == "__main__":
    cli()
