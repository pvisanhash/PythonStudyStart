from __future__ import annotations

import json
from pathlib import Path
from types import TracebackType

from .models import TaskBook


class TaskStorage:
    def __init__(self, path: Path):
        self.path = path
        self.book = TaskBook()

    def __enter__(self) -> TaskBook:
        self.book = self.load()
        return self.book

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            self.save(self.book)
        return False

    def load(self) -> TaskBook:
        if not self.path.exists():
            return TaskBook()

        text = self.path.read_text(encoding="utf-8")
        if not text.strip():
            return TaskBook()

        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("task data file must contain a JSON list")

        return TaskBook.from_json_data(data)

    def save(self, book: TaskBook) -> None:
        self.path.write_text(
            json.dumps(book.to_json_data(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

