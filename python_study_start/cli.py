from __future__ import annotations

import argparse
from pathlib import Path

from .models import InvalidPriorityError, TaskBook, TaskNotFoundError, VALID_PRIORITIES
from .report import render_stats, render_tasks, task_line
from .storage import TaskStorage
from .syntax_tour import run_tour

DEFAULT_DATA_FILE = Path(".study_tasks.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python-study-start",
        description="A runnable Python learning project: a tiny study task manager.",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="JSON file used to store tasks.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="add a study task")
    add_parser.add_argument("title")
    add_parser.add_argument(
        "--priority",
        choices=VALID_PRIORITIES,
        default="normal",
    )
    add_parser.add_argument("--tag", action="append", default=[])

    list_parser = subparsers.add_parser("list", help="list study tasks")
    list_parser.add_argument("--open-only", action="store_true")
    list_parser.add_argument("--tag")

    done_parser = subparsers.add_parser("done", help="mark a task as completed")
    done_parser.add_argument("task_id", type=int)

    delete_parser = subparsers.add_parser("delete", help="delete a task")
    delete_parser.add_argument("task_id", type=int)

    subparsers.add_parser("stats", help="show task statistics")
    subparsers.add_parser("demo", help="run a small in-memory demo")
    subparsers.add_parser("tour", help="run a guided syntax tour")

    return parser


def run_demo() -> None:
    book = TaskBook()
    book.add("Read variables and types", priority="high", tags={"python", "basic"})
    book.add("Write a function", priority="normal", tags={"python", "function"})
    book.add("Save data as JSON", priority="low", tags={"file"})
    book.mark_done(1)

    print(render_tasks(book.visible_tasks()))
    print()
    print(render_stats(book))


def handle_storage_command(args: argparse.Namespace) -> int:
    try:
        with TaskStorage(args.data_file) as book:
            match args.command:
                case "add":
                    task = book.add(
                        args.title,
                        priority=args.priority,
                        tags=set(args.tag),
                    )
                    print("Added:", task_line(task))
                case "list":
                    tasks = book.visible_tasks(
                        show_done=not args.open_only,
                        tag=args.tag,
                    )
                    print(render_tasks(tasks))
                case "done":
                    task = book.mark_done(args.task_id)
                    print("Completed:", task_line(task))
                case "delete":
                    task = book.delete(args.task_id)
                    print("Deleted:", task_line(task))
                case "stats":
                    print(render_stats(book))
                case _:
                    raise ValueError(f"unsupported command: {args.command}")
    except (InvalidPriorityError, TaskNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    match args.command:
        case "demo":
            run_demo()
            return 0
        case "tour":
            run_tour()
            return 0
        case _:
            return handle_storage_command(args)

