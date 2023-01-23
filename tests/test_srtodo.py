# tests/test_srtodo.py

import json
import pytest


from typer.testing import CliRunner
from srtodo import (__app_name__, __version__, cli, DB_READ_ERROR, SUCCESS, srtodo)


runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


@pytest.fixture
def mock_json_file(tmp_path):
    todo = [{'desc': 'get milk', 'prio': 2, 'done': False}]
    db_file = tmp_path / 'todo.json'
    with db_file.open('w') as db:
        json.dump(todo, db, indent=4)

    return db_file


test_data1 = {
        'desc': ['clean', 'the', 'house'],
        'prio': 1,
        'todo':{
            'desc': 'clean the house',
            'prio': 1,
            'done': False,
            },
        }

test_data2 = {
        'desc': ['Wash the car'],
        'prio': 2,
        'todo': {
            'desc': 'Wash the car.',
            'prio': 2,
            'done': False
            },
        }


@pytest.mark.parametrize(
    'desc, prio, expected',
    [
        pytest.param(
            test_data1['desc'],
            test_data1['prio'],
            (test_data1['todo'], SUCCESS),
        ),
        pytest.param(
            test_data2['desc'],
            test_data2['prio'],
            (test_data2['todo'], SUCCESS),
        ),
    ],
)

def test_add(mock_json_file, desc, prio, expected):
    todoer = srtodo.Todoer(mock_json_file)
    assert todoer.add(desc, prio) == expected
    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 2
