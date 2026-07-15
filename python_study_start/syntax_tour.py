from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from io import StringIO
from time import perf_counter

from .models import Priority, TaskBook
from .report import render_stats, render_tasks

# 第 6 阶段：语法导览
# 这个文件集中展示 Python 常见语法。建议在运行 tour 后，对照输出逐段阅读。


class StudyMode(Enum):
    # Enum（Enumeration，枚举）适合表示一组固定选项，避免到处手写字符串。
    READING = "reading"
    PRACTICE = "practice"
    REVIEW = "review"


@dataclass(frozen=True)
class StudySession:
    # frozen=True 表示创建后不能随便修改，更适合表示一次固定的学习安排。
    topic: str
    minutes: int
    mode: StudyMode = StudyMode.PRACTICE

    @property
    def label(self) -> str:
        return f"{self.topic} / {self.minutes} min / {self.mode.value}"

    @staticmethod
    def short(minutes: int) -> bool:
        # staticmethod 不依赖 self，适合放和这个类强相关的小工具函数。
        return minutes <= 15


class StrictTaskBook(TaskBook):
    # 继承：StrictTaskBook 复用了 TaskBook 的能力，只改造 add 这一小块行为。
    def add(
        self,
        title: str,
        priority: Priority = "normal",
        tags: set[str] | None = None,
    ):
        # any(...) 只要发现一个 True 就会停止，适合做“是否存在”的判断。
        if any(task.title == title for task in self.tasks):
            raise ValueError(f"duplicated task title: {title}")
        # super() 调用父类 TaskBook.add，避免重复写已有逻辑。
        return super().add(title, priority=priority, tags=tags)


@contextmanager
def fake_text_file(initial_text: str):
    """A tiny context manager that behaves like opening a text file."""
    file = StringIO(initial_text)
    try:
        # yield 前的代码相当于 __enter__，yield 后的 finally 相当于 __exit__。
        yield file
    finally:
        file.close()


def section(title: str) -> Callable:
    # 装饰器本质是“接收一个函数，返回一个新函数”。
    # 这里用它给每个语法章节自动打印标题和耗时。
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = perf_counter()
            print(f"\n== {title} ==")
            result = func(*args, **kwargs)
            elapsed_ms = (perf_counter() - start) * 1000
            print(f"(section finished in {elapsed_ms:.2f} ms)")
            return result

        return wrapper

    return decorator


def build_summary(title: str, *parts: str, uppercase: bool = False, **meta: str) -> str:
    # *parts 接收多个位置参数；**meta 接收多个关键字参数。
    body = " | ".join(parts)
    summary = f"{title}: {body}"
    if meta:
        summary += " | " + ", ".join(f"{key}={value}" for key, value in meta.items())
    return summary.upper() if uppercase else summary


async def fetch_tip(topic: str) -> str:
    # async/await 常用于网络请求、文件 IO 等等待型任务。
    # 这里 sleep(0) 只是演示语法，不是真的等待很久。
    await asyncio.sleep(0)
    return f"tip for {topic}: read, run, change, repeat"


@section("variables, strings, numbers, booleans, None")
def basic_values() -> None:
    # 类型标注不会强制改变运行方式，但能让编辑器和读者更容易理解代码。
    learner: str = "Ada"
    study_minutes: int = 25
    progress: float = 0.35
    has_focus: bool = True
    note: str | None = None

    print(f"{learner} will study for {study_minutes} minutes. Focus: {has_focus}")
    print("progress percent:", progress * 100)
    print("note is missing:", note is None)

    title = "Python syntax"
    # 字符串可以调用方法；切片 title[:6] 表示从开头取到下标 6 之前。
    print("lower/upper:", title.lower(), title.upper())
    print("slice:", title[:6], "| last char:", title[-1])
    print(
        "multiline:",
        """first line
second line""",
    )


@section("list, tuple, set, dict, unpacking")
def data_structures() -> None:
    topics = ["variables", "functions", "classes"]
    # 解包：把列表里的元素分配给多个变量；*rest 接住剩余元素。
    first, second, *rest = topics
    first_two: tuple[str, str] = (first, second)
    # 集合推导式会自动去重，所以 unique_letters 里不会有重复字母。
    unique_letters = {letter for topic in topics for letter in topic}
    scores = {"variables": 90, "functions": 85, "classes": 78}
    # {**dict1, **dict2} 是常见的字典合并写法。
    merged_scores = {**scores, "modules": 88}

    # list 是可变对象，可以 append/extend 修改内容。
    topics.append("modules")
    topics.extend(["files", "tests"])

    print("topics:", topics)
    print("first two:", first_two)
    print("rest:", rest)
    print("unique letter count:", len(unique_letters))
    print("merged scores:", merged_scores)
    print("dict items:", list(scores.items()))


@section("if, for, while, break, continue, comprehension")
def control_flow() -> None:
    numbers = [1, 2, 3, 4, 5]
    # 列表推导式：[结果 for 元素 in 可迭代对象 if 条件]。
    squares = [number * number for number in numbers if number % 2 == 1]
    print("odd squares:", squares)

    for index, number in enumerate(numbers, start=1):
        if number == 2:
            # continue 跳过本轮循环，继续下一轮。
            continue
        if number > 4:
            # break 直接结束整个循环。
            break
        print(f"#{index}: {number}")

    countdown = 3
    while countdown > 0:
        print("countdown:", countdown)
        countdown -= 1
    else:
        # while 的 else 会在循环自然结束时执行；如果被 break 打断则不执行。
        print("while loop finished normally")


@section("functions, defaults, *args, **kwargs, lambda")
def function_shapes() -> None:
    summary = build_summary(
        "Plan",
        "variables",
        "functions",
        "classes",
        uppercase=False,
        owner="Ada",
        day="Monday",
    )
    print(summary)

    sessions = [
        StudySession("variables", 10, StudyMode.READING),
        StudySession("functions", 25),
        StudySession("classes", 20, StudyMode.REVIEW),
    ]
    by_minutes = sorted(sessions, key=lambda session: session.minutes)
    # lambda 是一个小型匿名函数，常用于排序、过滤这类短逻辑。
    short_topics = [
        session.topic for session in sessions if StudySession.short(session.minutes)
    ]

    print("sorted:", [session.label for session in by_minutes])
    print("short sessions:", short_topics)


@section("functions, class, inheritance, dataclass, generator")
def project_objects() -> None:
    book = StrictTaskBook()
    # 这里调用的是 StrictTaskBook.add；内部又会通过 super() 调用 TaskBook.add。
    book.add("Read Python basics", priority="high", tags={"python", "basic"})
    book.add("Practice file IO", tags={"python", "file"})
    book.mark_done(1)
    print(render_tasks(book.visible_tasks()))
    print(render_stats(book))

    # TaskBook.by_tag uses yield, so it returns a generator that produces items lazily.
    print("python tag titles:", [task.title for task in book.by_tag("python")])

    if open_tasks := book.visible_tasks(show_done=False):
        # 海象运算符 := 可以在判断条件里同时完成赋值。
        print("walrus found open tasks:", len(open_tasks))


@section("match, guards, exception handling")
def pattern_matching() -> None:
    command = ("list", {"open_only": True})

    try:
        # match/case 可以匹配普通值、tuple、dict，也可以加 if guard。
        match command:
            case ("list", {"open_only": True}):
                print("Show open tasks")
            case ("list", _):
                print("Show all tasks")
            case ("stats", _):
                print("Show statistics")
            case (name, _) if isinstance(name, str):
                raise ValueError(f"Unknown command: {name}")
            case other:
                raise ValueError(f"Unknown command: {other}")
    except ValueError as error:
        print("handled error:", error)
    else:
        print("no error happened")
    finally:
        print("cleanup always runs")


@section("with, context manager, file-like object")
def context_manager_demo() -> None:
    # with 适合管理需要“用完清理”的资源，比如文件、网络连接、锁。
    with fake_text_file("task one\ntask two\n") as file:
        lines = [line.strip() for line in file if line.strip()]

    print("loaded lines:", lines)


@section("async, await")
def async_demo() -> None:
    tip = asyncio.run(fetch_tip("functions"))
    print(tip)


def run_tour() -> None:
    # 按“从基础到进阶”的顺序运行每个章节。
    basic_values()
    data_structures()
    control_flow()
    function_shapes()
    project_objects()
    pattern_matching()
    context_manager_demo()
    async_demo()
