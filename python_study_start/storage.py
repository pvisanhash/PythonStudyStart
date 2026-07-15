from __future__ import annotations

import json
from pathlib import Path
from types import TracebackType

from .models import TaskBook


# 第 4 阶段：文件持久化
# “持久化”就是把内存里的数据保存到文件，下次运行还能读回来。
class TaskStorage:
    def __init__(self, path: Path):
        self.path = path
        self.book = TaskBook()

    def __enter__(self) -> TaskBook:
        # 进入 with 代码块时读取文件，返回一个可操作的 TaskBook。
        self.book = self.load()
        return self.book

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        # 如果 with 代码块没有异常，就保存数据；有异常时不保存，避免写入坏数据。
        if exc_type is None:
            self.save(self.book)
        # 返回 False 表示：如果真的有异常，不吞掉它，继续交给外层处理。
        return False

    def load(self) -> TaskBook:
        # 第一次运行时文件不存在，直接返回空任务本。
        if not self.path.exists():
            return TaskBook()

        text = self.path.read_text(encoding="utf-8")
        # 文件存在但内容为空，也当作空任务本处理。
        if not text.strip():
            return TaskBook()

        # json.loads 把字符串解析成 Python 数据结构。
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("task data file must contain a JSON list")

        return TaskBook.from_json_data(data)

    def save(self, book: TaskBook) -> None:
        # json.dumps 把 Python 数据结构转换成 JSON 字符串。
        # ensure_ascii=False 让中文保持可读，不被转成 \u4e2d 这类形式。
        self.path.write_text(
            json.dumps(book.to_json_data(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
