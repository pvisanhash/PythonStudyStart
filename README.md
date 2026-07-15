# Python Study Start

一个给 Python 初学者快速上手的小工程。它不是“题目 + 答案”，而是一个真正能运行的命令行项目：**学习任务管理器**。

你可以添加学习任务、标记完成、按标签筛选、查看统计，数据会保存到本地 JSON 文件。代码里自然覆盖了 Python 常见语法：变量、字符串、数字、布尔值、`None`、类型标注、列表/字典/集合/元组、切片、解包、条件判断、`for`/`while` 循环、`break`/`continue`、推导式、函数、默认参数、关键字参数、`*args`、`**kwargs`、`lambda`、异常、`try/except/else/finally`、类、继承式思维、`dataclass`、`Enum`、属性、静态方法、模块拆分、导入、文件读写、上下文管理器、命令行参数、`match` 模式匹配、生成器、装饰器、海象运算符、`async`/`await` 和单元测试。

## 准备

本项目使用 `uv` 管理。

```bash
uv sync
```

## 运行

查看帮助：

```bash
uv run python -m python_study_start --help
```

运行内置演示，快速看到项目效果：

```bash
uv run python -m python_study_start demo
```

添加任务：

```bash
uv run python -m python_study_start add "学习函数" --priority high --tag python --tag basic
```

查看任务：

```bash
uv run python -m python_study_start list
```

完成任务：

```bash
uv run python -m python_study_start done 1
```

查看统计：

```bash
uv run python -m python_study_start stats
```

运行语法导览：

```bash
uv run python -m python_study_start tour
```

## 运行测试

```bash
uv run python -m unittest
```

## 建议阅读顺序

如果你是小白，建议按这个顺序读，不要一上来就把所有文件都啃完：

1. `python_study_start/__main__.py`：先理解程序从哪里开始运行。
2. `python_study_start/cli.py`：再看命令行参数如何转成程序行为。
3. `python_study_start/models.py`：学习变量、类型标注、类、方法、异常和数据结构。
4. `python_study_start/report.py`：学习字符串格式化和把数据渲染成文本。
5. `python_study_start/storage.py`：学习文件读写、JSON 和上下文管理器。
6. `python_study_start/syntax_tour.py`：集中复习常见 Python 语法，从基础看到进阶。
7. `tests/test_taskbook.py`：最后看单元测试，理解如何验证代码行为。

每个主要源码文件里都加了“第几阶段”的注释。阅读时可以先看注释，再运行命令观察输出，最后尝试改一两行代码。

## 语法导览覆盖点

运行 `tour` 后，对照 `python_study_start/syntax_tour.py` 阅读：

- 基础值：变量、字符串、数字、布尔值、`None`、f-string、多行字符串、切片。
- 数据结构：list、tuple、set、dict、解包、`*rest`、字典合并、遍历 `items()`。
- 控制流：`if`、`for`、`while`、`else`、`break`、`continue`、`enumerate()`、列表/集合推导式。
- 函数：类型标注、默认参数、关键字参数、`*args`、`**kwargs`、`lambda`。
- 面向对象：class、`dataclass`、`Enum`、属性、静态方法、实例方法。
- 工程语法：模块导入、包入口、命令行参数、JSON、文件路径、上下文管理器。
- 进阶语法：装饰器、生成器、`yield`、`match case`、guard、海象运算符、`async`/`await`。
- 质量保障：`unittest`、异常断言、行为测试。

默认数据文件是 `.study_tasks.json`，可以用 `--data-file` 指定其他位置。
