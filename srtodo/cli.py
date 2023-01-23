# This module provides the RP To-Do CLI.
# srtodo/cli.py


from typing import Optional, List
from pathlib import Path

import typer

from srtodo import (
        ERRORS,__version__, __app_name__, config, database, srtodo
        )

app = typer.Typer()

@app.command()
def init(
        db_path: str = typer.Option(
            str(database.DEFAULT_DB_FILE_PATH),
            '--db-path',
            '-db',
            prompt='to-do database location?',
    ),
) -> None:
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
                f'Creating config file failed with "{ERRORS[app_init_error]}"',
                fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))

    if db_init_error:
        typer.secho(
                f'Creating database failed with "{ERRORS[db_init_error]}"',
                fg=typer.colors.RED
        )
        raise typer.Exit(1)
    else:
        typer.secho(f'The to-do database is {db_path}', fg=typer.colors.GREEN)


def get_todoer() -> srtodo.Todoer:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
                'config file not found. please run "srtodo init"',
                fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if db_path.exists():
      return srtodo.Todoer(db_path)

    else:
        typer.secho(
                'database not found. please run "srtodo init"',
                fg=typer.colors.RED,
                )
        raise typer.Exit(1)

@app.command()
def add(
        desc: List[str] = typer.Argument(...),
        prio: int = typer.Option(2, '--prio', '-p', min=1, max=3),
        ) -> None:
    # ADD A NEW WITH DESC
    todoer = get_todoer()
    todo, error = todoer.add(desc, prio)
    if error:
        typer.secho(
                    f'Adding to-do failed with error {ERRORS[error]}',
                    fg=typer.colors.RED,
                    )

        raise typer.Exit(1)
    else:
        typer.secho(
                f"""todo: {todo['desc']} was added """
                f"""with prio: {prio}""",
                fg=typer.colors.GREEN,
                )


@app.command(name='list')
def list_all() -> None:
    todoer = get_todoer()
    todo_list = todoer.get_todo_list()

    if len(todo_list) == 0:
        typer.secho(
                'There are no tasks in your todo-list', fg=typer.colors.RED,)
        raise typer.Exit

    typer.secho('\ntodo list: \n', fg=typer.colors.BLUE, bold=True)
    columns = (
            'ID.',
            '| PRIO ',
            '| DONE  ',
            '| DESC ',
            )

    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho('-' * len(headers), fg=typer.colors.BLUE)
    for id, todo in enumerate(todo_list, 1):
        desc, prio, done = todo.values()
        typer.secho(
                f'{id}{(len(columns[0]) - len(str(id))) * " "}'
                f'| ({prio}) {(len(columns[1]) - len(str(prio)) - 5) * " "}'
                f'| {done} {(len(columns[2]) - len(str(done)) - 3) * " "}'
                f'| {desc} {(len(columns[3]) - len(desc)) * " "}'
                , fg=typer.colors.BLUE)

        typer.secho('-' * len(headers) + '\n', fg=typer.colors.BLUE)


@app.command(name='complete')
def set_done(todo_id: int = typer.Argument(...)) -> None:
    todoer = get_todoer()
    todo, error = todoer.set_done(todo_id)
    if error:
        typer.secho(
            f'Completing to-do #{todo_id}, failed with error: {ERRORS[error]}',
            fg=typer.colors.RED
        )
    else:
        typer.secho(
            f"""Completed to-do #{todo_id}, "{todo['desc']}""",
            fg=typer.colors.GREEN
        )


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.command(name='remove')
def remove(
        todo_id: int = typer.Argument(...),
        force: bool = typer.Option(False,
            '--force', '-f',
            help='Force deletation without confirmation',),
) -> None:
    todoer = get_todoer()

    def _remove():
        todo, error = todoer.remove(todo_id)
        if error:
            typer.secho(
                f'Removing to-do # {todo_id} failed with {ERRORS[error]}',
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f'todo #{todo_id}: {todo["desc"]} removed successfully',
                fg=typer.colors.GREEN,
            )

    if force:
        _remove()
    else:
        todo_list = todoer.get_todo_list()
        try:
            todo = todo_list[todo_id-1]
        except IndexError:
            typer.secho('Inalid TODO_ID', fg=typer.colors.RED)
            raise typer.Exit(1)

        delete = typer.confirm(
            f'Delete to-do # {todo_id}: {todo["desc"]}?'
        )

        if delete:
            _remove()
        else:
            typer.echo('Operation cancelled')


@app.callback()
def main(
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            "-v",
            help="Show the application's version and exit.",
            callback=_version_callback,
            is_eager=True,
        )
) -> None:
    return
