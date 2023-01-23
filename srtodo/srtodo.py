# This module provides the model-controller
# srtodo/srtodo.py

from pathlib import Path
from typing import Any, List, Dict, NamedTuple

from srtodo.database import DatabaseHandler
from srtodo import DB_READ_ERROR, ID_ERROR


class CurrentToDo(NamedTuple):
    todo: Dict[str, Any]
    error: int


class Todoer:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, desc: List[str], prio: int = 2) -> CurrentToDo:
        # Adding a new to do point in the db
        description_text = ' '.join(desc)
        if not description_text.endswith('.'):
            description_text += '.'

        todo = {
                'desc': description_text,
                'prio': prio,
                'done': False,
        }

        read = self._db_handler.read_todos()
        if read.error == DB_READ_ERROR:
            return CurrentToDo(todo, read.error)
        read.todo_list.append(todo)

        write = self._db_handler.write_todos(read.todo_list)

        return CurrentToDo(todo, write.error)

    def get_todo_list(self) -> List[Dict[str, Any]]:
        read = self._db_handler.read_todos()
        return read.todo_list

    def set_done(self, todo_id: int) -> CurrentToDo:
        read = self._db_handler.read_todos()
        if read.error:
            return CurrentToDo({}, read.error)
        try:
            todo = read.todo_list[todo_id - 1]
        except IndexError:
            return CurrentToDo({}, ID_ERROR)
        todo['done'] = True
        write = self._db_handler.write_todos(read.todo_list)

        return CurrentToDo(todo, write.error)

    def remove(self, todo_id: int) -> CurrentToDo:
        read = self._db_handler.read_todos()
        if read.error:
            return CurrentToDo({}, read.error)
        try:
            todo = read.todo_list.pop(todo_id-1)
        except IndexError:
            return CurrentToDo({}, ID_ERROR)
        write = self._db_handler.write_todos(read.todo_list)

        return CurrentToDo(todo, write.error)
