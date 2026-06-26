from __future__ import annotations

from .models import Task, TaskBook

PRIORITY_LABELS = {
    "low": "LOW",
    "normal": "NORMAL",
    "high": "HIGH",
}


def task_line(task: Task) -> str:
    tags = ", ".join(sorted(task.tags)) if task.tags else "no tags"
    priority = PRIORITY_LABELS[task.priority]
    return f"[{task.status_icon}] #{task.id:<3} {priority:<6} {task.title} ({tags})"


def render_tasks(tasks: list[Task]) -> str:
    if not tasks:
        return "No tasks found."
    return "\n".join(task_line(task) for task in tasks)


def render_stats(book: TaskBook) -> str:
    stats = book.stats()
    rows = [
        ("Total", stats["total"]),
        ("Open", stats["open"]),
        ("Completed", stats["completed"]),
        ("Open high priority", stats["high_open"]),
        ("Unique tags", stats["unique_tags"]),
    ]
    return "\n".join(f"{name:<18}: {value}" for name, value in rows)

