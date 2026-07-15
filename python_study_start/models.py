from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Priority = Literal["low", "normal", "high"]

# 第 3 阶段：数据模型
# 这里不关心命令行，也不关心文件，只描述“任务”本身和任务列表的行为。

VALID_PRIORITIES: tuple[Priority, ...] = ("low", "normal", "high")


class TaskNotFoundError(Exception):
    """Raised when the user asks for a task id that does not exist."""


class InvalidPriorityError(ValueError):
    """Raised when a priority is outside the allowed values."""


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


@dataclass
class Task:
    # dataclass 会根据这些字段自动生成 __init__ 等方法，减少样板代码。
    id: int
    title: str
    priority: Priority = "normal"
    # default_factory 用来创建可变默认值；否则多个 Task 可能会共用同一个 set。
    tags: set[str] = field(default_factory=set)
    done: bool = False
    created_at: str = field(default_factory=now_text)

    def __post_init__(self) -> None:
        # __post_init__ 会在 dataclass 自动生成的 __init__ 执行后运行，
        # 常用于做数据校验和清洗。
        if self.priority not in VALID_PRIORITIES:
            raise InvalidPriorityError(
                f"priority must be one of {', '.join(VALID_PRIORITIES)}"
            )
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title cannot be empty")

    @property
    def status_icon(self) -> str:
        # @property 让方法像属性一样访问：task.status_icon，而不是 task.status_icon()。
        return "x" if self.done else " "

    def to_dict(self) -> dict[str, object]:
        # JSON（JavaScript Object Notation，JavaScript 对象表示法）没有 set 类型，
        # 所以这里把 tags 转成排序后的 list，方便保存到文件。
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "tags": sorted(self.tags),
            "done": self.done,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Task:
        # classmethod 常用于“从外部数据重新构造对象”。
        # cls 表示当前类，比直接写 Task 更灵活。
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            priority=str(data.get("priority", "normal")),  # type: ignore[arg-type]
            tags=set(map(str, data.get("tags", []))),
            done=bool(data.get("done", False)),
            created_at=str(data.get("created_at", now_text())),
        )


@dataclass
class TaskBook:
    # TaskBook 是一个小型“任务仓库”，负责管理多个 Task。
    tasks: list[Task] = field(default_factory=list)

    def __len__(self) -> int:
        # 定义 __len__ 后，就可以写 len(book)。
        return len(self.tasks)

    def __iter__(self):
        # 定义 __iter__ 后，就可以直接 for task in book。
        return iter(self.tasks)

    @property
    def next_id(self) -> int:
        # 用现有最大 id + 1 生成下一个任务 id。
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def add(
        self,
        title: str,
        priority: Priority = "normal",
        tags: set[str] | None = None,
    ) -> Task:
        # 先创建 Task 对象，再加入列表，最后把新任务返回给调用者。
        task = Task(
            id=self.next_id,
            title=title,
            priority=priority,
            tags=tags or set(),
        )
        self.tasks.append(task)
        return task

    def find(self, task_id: int) -> Task:
        # for 循环逐个检查任务，找到就提前 return。
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"task #{task_id} does not exist")

    def mark_done(self, task_id: int) -> Task:
        task = self.find(task_id)
        task.done = True
        return task

    def delete(self, task_id: int) -> Task:
        task = self.find(task_id)
        self.tasks.remove(task)
        return task

    def by_tag(self, tag: str):
        # yield 会创建生成器：需要一个任务才产出一个任务，不会先构造完整列表。
        for task in self.tasks:
            if tag in task.tags:
                yield task

    def visible_tasks(
        self,
        show_done: bool = True,
        tag: str | None = None,
    ) -> list[Task]:
        # 条件表达式：如果提供了 tag，就按标签过滤；否则使用全部任务。
        source = self.by_tag(tag) if tag else self.tasks
        # 列表推导式：把“遍历 + 条件过滤 + 生成新列表”写在一行里。
        return [task for task in source if show_done or not task.done]

    def stats(self) -> dict[str, int]:
        # sum(...) 常和生成器表达式配合，用来统计满足条件的数量。
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.done)
        open_count = total - completed
        high_open = sum(
            1 for task in self.tasks if task.priority == "high" and not task.done
        )
        unique_tags = {tag for task in self.tasks for tag in task.tags}
        return {
            "total": total,
            "completed": completed,
            "open": open_count,
            "high_open": high_open,
            "unique_tags": len(unique_tags),
        }

    def to_json_data(self) -> list[dict[str, object]]:
        return [task.to_dict() for task in self.tasks]

    @classmethod
    def from_json_data(cls, data: list[dict[str, object]]) -> TaskBook:
        return cls(tasks=[Task.from_dict(item) for item in data])
