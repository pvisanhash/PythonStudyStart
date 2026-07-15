from __future__ import annotations

from .models import Task, TaskBook

# 第 5 阶段：输出格式
# 这里专门负责“把数据变成人能读的文字”，不修改任务数据。

PRIORITY_LABELS = {
    "low": "LOW",
    "normal": "NORMAL",
    "high": "HIGH",
}


def task_line(task: Task) -> str:
    # 三元表达式：条件成立用左边，否则用右边。
    tags = ", ".join(sorted(task.tags)) if task.tags else "no tags"
    priority = PRIORITY_LABELS[task.priority]
    # f-string 里的 :<3 / :<6 表示左对齐并占固定宽度，让输出更整齐。
    return f"[{task.status_icon}] #{task.id:<3} {priority:<6} {task.title} ({tags})"


def render_tasks(tasks: list[Task]) -> str:
    if not tasks:
        return "No tasks found."
    # "\n".join(...) 把多行文本拼成一个字符串，中间用换行符连接。
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
    # 这里用列表里的 tuple 保存“显示名称 + 数值”，再统一渲染。
    return "\n".join(f"{name:<18}: {value}" for name, value in rows)
