"""
Aplicación de consola para gestionar una lista de tareas (To-Do list).

La información se persiste en un archivo CSV llamado `todos.csv` con la
estructura: id,title,status
"""

import csv
import os

CSV_FILE = "todos.csv"
FIELDNAMES = ["id", "title", "status"]

# Lista en memoria que contiene las tareas mientras el programa se ejecuta.
todos = []


def load_todos():
    """
    Carga las tareas desde el archivo `todos.csv` y las guarda en la
    lista global `todos`. Si el archivo no existe, lo crea vacío con
    su cabecera correspondiente.
    """
    global todos
    todos = []

    if not os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
                writer.writeheader()
        except OSError as error:
            print(f"No se pudo crear el archivo {CSV_FILE}: {error}")
        return

    try:
        with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                todos.append({
                    "id": row.get("id"),
                    "title": row.get("title"),
                    "status": row.get("status", "pendiente"),
                })
    except (OSError, csv.Error) as error:
        print(f"Ocurrió un error al leer {CSV_FILE}: {error}")


def save_todos():
    """
    Guarda el estado actual de la lista `todos` en el archivo `todos.csv`,
    sobrescribiendo su contenido previo.
    """
    try:
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(todos)
    except OSError as error:
        print(f"No se pudo guardar la lista en {CSV_FILE}: {error}")


def add_one_task(title):
    """
    Agrega una nueva tarea a la lista `todos` con estado "pendiente".

    Parámetros:
        title (str): título/descripción de la tarea a agregar.
    """
    title = (title or "").strip()

    if not title:
        print("El título de la tarea no puede estar vacío.")
        return

    new_id = (int(todos[-1]["id"]) + 1) if todos else 1
    todos.append({"id": str(new_id), "title": title, "status": "pendiente"})
    print(f"Tarea '{title}' agregada correctamente.")


def print_list():
    """
    Imprime en consola la lista numerada de tareas con su estado.
    Si la lista está vacía, muestra un mensaje informativo.
    """
    if not todos:
        print("No hay tareas registradas todavía.")
        return

    print("\n--- Lista de tareas ---")
    for index, task in enumerate(todos, start=1):
        print(f"{index}. {task['title']} [{task['status']}]")
    print("-----------------------\n")


def delete_task(number_to_delete):
    """
    Elimina la tarea correspondiente al número (posición) indicado.

    Parámetros:
        number_to_delete: número de la tarea a eliminar, tal como se
            muestra en `print_list` (base 1). Puede venir como str.
    """
    try:
        index = int(number_to_delete) - 1
    except (TypeError, ValueError):
        print("Debes ingresar un número entero válido.")
        return

    if index < 0 or index >= len(todos):
        print("No existe una tarea con ese número.")
        return

    removed = todos.pop(index)
    print(f"Tarea '{removed['title']}' eliminada correctamente.")


def show_menu():
    """Muestra el menú principal de opciones disponibles."""
    print("Menú de tareas:")
    print("1. Ver tareas")
    print("2. Agregar tarea")
    print("3. Eliminar tarea")
    print("4. Salir")


def main():
    """Bucle principal de la aplicación de consola."""
    load_todos()

    while True:
        show_menu()
        option = input("Elige una opción (1-4): ").strip()

        if option == "1":
            print_list()
        elif option == "2":
            title = input("Título de la nueva tarea: ")
            add_one_task(title)
        elif option == "3":
            print_list()
            number = input("Número de la tarea a eliminar: ")
            delete_task(number)
        elif option == "4":
            save_todos()
            print("Tareas guardadas. ¡Hasta luego!")
            break
        else:
            print("Opción inválida, intenta de nuevo.\n")


if __name__ == "__main__":
    main()
