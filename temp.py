# Just testing some things, nothing special

import typer
import json
import configparser

app = typer.Typer()

@app.command()
def hello(name: str):
    print(f'HELLO {name}')


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f'Good bye my formal love {name}')
    else:
        print(f'Bye bitch, {name}')

@app.command()
def headline(text: str, align:bool = False):
    if align:
        print(f"{text.title()}\n{'-' * len(text)}")
    else:
        print(f" {text.title()} ".center(50,"#")) 


if __name__ == '__main__':
    app()


