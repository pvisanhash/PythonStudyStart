from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

Priority = Literal["low", "normal", "high"]

VALID_PRIORITIES: tuple[Priority, ...] = ("low", "normal", "high")


class TaskNotFoundError(Exception):
    """Raised when the user asks for a task id that does not exist."""


class InvalidPriorityError(ValueError):
    """Raised when a priority is outside the allowed values."""


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


@dataclass
class Task:
    id: int
    title: str
    priority: Priority = "normal"
    # Use default_factory for mutable values; otherwise different tasks would
    # accidentally share the same set object.
    tags: set[str] = field(default_factory=set)
    done: bool = False
    created_at: str = field(default_factory=now_text)

    def __post_init__(self) -> None:
        if self.priority not in VALID_PRIORITIES:
            raise InvalidPriorityError(
                f"priority must be one of {', '.join(VALID_PRIORITIES)}"
            )
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title cannot be empty")

    @property
    def status_icon(self) -> str:
        return "x" if self.done else " "

    def to_dict(self) -> dict[str, object]:
        # JSON does not have a set type, so tags are converted to a sorted list.
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
        # A classmethod is a common place to rebuild an object from external data.
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
    tasks: list[Task] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.tasks)

    def __iter__(self):
        return iter(self.tasks)

    @property
    def next_id(self) -> int:
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    def add(
        self,
        title: str,
        priority: Priority = "normal",
        tags: set[str] | None = None,
    ) -> Task:
        task = Task(
            id=self.next_id,
            title=title,
            priority=priority,
            tags=tags or set(),
        )
        self.tasks.append(task)
        return task

    def find(self, task_id: int) -> Task:
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
        # yield creates a generator, so callers can iterate without building
        # a temporary list first.
        for task in self.tasks:
            if tag in task.tags:
                yield task

    def visible_tasks(
        self,
        show_done: bool = True,
        tag: str | None = None,
    ) -> list[Task]:
        source = self.by_tag(tag) if tag else self.tasks
        return [task for task in source if show_done or not task.done]

    def stats(self) -> dict[str, int]:
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
