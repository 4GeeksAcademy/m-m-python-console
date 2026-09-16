"""
Tests automatizados para la aplicación de consola To-Do (`app.py`).

Cada test se ejecuta de forma aislada: la constante `app.CSV_FILE` se
redirige a un archivo temporal y la lista global `app.todos` se reinicia,
de modo que el `todos.csv` real del proyecto nunca se modifica.
"""

import csv
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app


@pytest.fixture(autouse=True)
def isolated_csv(tmp_path, monkeypatch):
    """Aísla el CSV y la lista en memoria antes de cada test."""
    csv_path = tmp_path / "todos.csv"
    monkeypatch.setattr(app, "CSV_FILE", str(csv_path))
    monkeypatch.setattr(app, "todos", [])
    return csv_path


def write_csv(csv_path, rows):
    """Helper: escribe un CSV de tareas con la cabecera esperada."""
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=app.FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def test_load_todos_creates_file_with_header(isolated_csv):
    assert not isolated_csv.exists()

    app.load_todos()

    assert isolated_csv.exists()
    assert isolated_csv.read_text(encoding="utf-8").splitlines()[0] == "id,title,status"
    assert app.todos == []


def test_load_todos_reads_existing_tasks(isolated_csv):
    write_csv(isolated_csv, [
        {"id": "1", "title": "Comprar pan", "status": "pendiente"},
        {"id": "2", "title": "Estudiar Python", "status": "completada"},
    ])

    app.load_todos()

    assert app.todos == [
        {"id": "1", "title": "Comprar pan", "status": "pendiente"},
        {"id": "2", "title": "Estudiar Python", "status": "completada"},
    ]


def test_save_todos_roundtrip(isolated_csv):
    app.todos.append({"id": "1", "title": "Regar plantas", "status": "pendiente"})

    app.save_todos()
    app.load_todos()

    assert isolated_csv.exists()
    assert app.todos == [{"id": "1", "title": "Regar plantas", "status": "pendiente"}]


def test_add_one_task_assigns_incremental_id():
    app.add_one_task("Primera tarea")
    app.add_one_task("Segunda tarea")

    assert app.todos == [
        {"id": "1", "title": "Primera tarea", "status": "pendiente"},
        {"id": "2", "title": "Segunda tarea", "status": "pendiente"},
    ]


@pytest.mark.parametrize("title", ["", "   ", None])
def test_add_one_task_rejects_empty_title(title, capsys):
    app.add_one_task(title)

    assert app.todos == []
    assert "no puede estar vacío" in capsys.readouterr().out


def test_print_list_when_empty(capsys):
    app.print_list()

    assert "No hay tareas registradas" in capsys.readouterr().out


def test_print_list_shows_numbered_tasks(capsys):
    app.add_one_task("Comprar pan")
    app.add_one_task("Estudiar Python")
    capsys.readouterr()  # descarta la salida de add_one_task

    app.print_list()

    output = capsys.readouterr().out
    assert "1. Comprar pan [pendiente]" in output
    assert "2. Estudiar Python [pendiente]" in output


def test_delete_task_removes_by_displayed_number():
    app.add_one_task("Comprar pan")
    app.add_one_task("Estudiar Python")

    app.delete_task(1)

    assert [task["title"] for task in app.todos] == ["Estudiar Python"]


def test_delete_task_with_invalid_input(capsys):
    app.add_one_task("Comprar pan")
    capsys.readouterr()

    app.delete_task("abc")

    assert len(app.todos) == 1
    assert "número entero válido" in capsys.readouterr().out


@pytest.mark.parametrize("number", [0, 99, -1])
def test_delete_task_out_of_range(number, capsys):
    app.add_one_task("Comprar pan")
    capsys.readouterr()

    app.delete_task(number)

    assert len(app.todos) == 1
    assert "No existe una tarea con ese número" in capsys.readouterr().out
