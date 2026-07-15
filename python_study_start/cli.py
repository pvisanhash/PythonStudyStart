from __future__ import annotations

import argparse
from pathlib import Path

from .models import InvalidPriorityError, TaskBook, TaskNotFoundError, VALID_PRIORITIES
from .report import render_stats, render_tasks, task_line
from .storage import TaskStorage
from .syntax_tour import run_tour

# 第 2 阶段：命令行入口
# 这个文件负责把用户输入的命令转换成程序里的函数调用。
# 例如：
#   uv run python -m python_study_start add "学习函数" --priority high
# 会被 argparse 解析成 command="add"、title="学习函数"、priority="high"。

DEFAULT_DATA_FILE = Path(".study_tasks.json")


def build_parser() -> argparse.ArgumentParser:
    # argparse 是 Python 标准库里的命令行解析工具。
    # 它会帮我们处理 --help、参数类型、子命令等常见工作。
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

    # subparsers 表示“子命令”，例如 add/list/done/delete/stats。
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="add a study task")
    # 不带 -- 的参数叫位置参数，用户必须提供。
    add_parser.add_argument("title")
    add_parser.add_argument(
        "--priority",
        # choices 会限制用户只能输入 low/normal/high。
        choices=VALID_PRIORITIES,
        default="normal",
    )
    # action="append" 表示 --tag 可以重复出现多次，最后得到一个列表。
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
    # demo 使用内存里的 TaskBook，不读写本地文件，适合初学者先看运行效果。
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
        # with 会自动调用 TaskStorage.__enter__ 读取数据，
        # 代码块正常结束后再调用 __exit__ 保存数据。
        with TaskStorage(args.data_file) as book:
            # match/case 是 Python 3.10+ 的模式匹配，适合分发不同命令。
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
        # 捕获可预期错误，给用户友好的提示，而不是打印一大段异常堆栈。
        print(f"Error: {error}")
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    # argv 默认是 None，argparse 会自动读取真实命令行参数。
    # 测试时也可以传入一个列表，模拟用户输入。
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
