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


class StudyMode(Enum):
    READING = "reading"
    PRACTICE = "practice"
    REVIEW = "review"


@dataclass(frozen=True)
class StudySession:
    topic: str
    minutes: int
    mode: StudyMode = StudyMode.PRACTICE

    @property
    def label(self) -> str:
        return f"{self.topic} / {self.minutes} min / {self.mode.value}"

    @staticmethod
    def short(minutes: int) -> bool:
        return minutes <= 15


class StrictTaskBook(TaskBook):
    def add(
        self,
        title: str,
        priority: Priority = "normal",
        tags: set[str] | None = None,
    ):
        if any(task.title == title for task in self.tasks):
            raise ValueError(f"duplicated task title: {title}")
        return super().add(title, priority=priority, tags=tags)


@contextmanager
def fake_text_file(initial_text: str):
    """A tiny context manager that behaves like opening a text file."""
    file = StringIO(initial_text)
    try:
        yield file
    finally:
        file.close()


def section(title: str) -> Callable:
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
    body = " | ".join(parts)
    summary = f"{title}: {body}"
    if meta:
        summary += " | " + ", ".join(f"{key}={value}" for key, value in meta.items())
    return summary.upper() if uppercase else summary


async def fetch_tip(topic: str) -> str:
    await asyncio.sleep(0)
    return f"tip for {topic}: read, run, change, repeat"


@section("variables, strings, numbers, booleans, None")
def basic_values() -> None:
    learner: str = "Ada"
    study_minutes: int = 25
    progress: float = 0.35
    has_focus: bool = True
    note: str | None = None

    print(f"{learner} will study for {study_minutes} minutes. Focus: {has_focus}")
    print("progress percent:", progress * 100)
    print("note is missing:", note is None)

    title = "Python syntax"
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
    first, second, *rest = topics
    first_two: tuple[str, str] = (first, second)
    unique_letters = {letter for topic in topics for letter in topic}
    scores = {"variables": 90, "functions": 85, "classes": 78}
    merged_scores = {**scores, "modules": 88}

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
    squares = [number * number for number in numbers if number % 2 == 1]
    print("odd squares:", squares)

    for index, number in enumerate(numbers, start=1):
        if number == 2:
            continue
        if number > 4:
            break
        print(f"#{index}: {number}")

    countdown = 3
    while countdown > 0:
        print("countdown:", countdown)
        countdown -= 1
    else:
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
    short_topics = [
        session.topic for session in sessions if StudySession.short(session.minutes)
    ]

    print("sorted:", [session.label for session in by_minutes])
    print("short sessions:", short_topics)


@section("functions, class, inheritance, dataclass, generator")
def project_objects() -> None:
    book = StrictTaskBook()
    book.add("Read Python basics", priority="high", tags={"python", "basic"})
    book.add("Practice file IO", tags={"python", "file"})
    book.mark_done(1)
    print(render_tasks(book.visible_tasks()))
    print(render_stats(book))

    # TaskBook.by_tag uses yield, so it returns a generator that produces items lazily.
    print("python tag titles:", [task.title for task in book.by_tag("python")])

    if open_tasks := book.visible_tasks(show_done=False):
        print("walrus found open tasks:", len(open_tasks))


@section("match, guards, exception handling")
def pattern_matching() -> None:
    command = ("list", {"open_only": True})

    try:
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
    with fake_text_file("task one\ntask two\n") as file:
        lines = [line.strip() for line in file if line.strip()]

    print("loaded lines:", lines)


@section("async, await")
def async_demo() -> None:
    tip = asyncio.run(fetch_tip("functions"))
    print(tip)


def run_tour() -> None:
    basic_values()
    data_structures()
    control_flow()
    function_shapes()
    project_objects()
    pattern_matching()
    context_manager_demo()
    async_demo()
