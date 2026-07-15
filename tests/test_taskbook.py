import unittest

from python_study_start.models import InvalidPriorityError, TaskBook, TaskNotFoundError


# 第 7 阶段：测试
# 测试不是给机器看的“额外作业”，而是用代码描述“程序应该怎么工作”。
class TaskBookTest(unittest.TestCase):
    def test_add_and_complete_task(self):
        # Arrange：准备测试数据。
        book = TaskBook()

        # Act：执行要测试的行为。
        task = book.add("Learn functions", priority="high", tags={"python"})
        completed = book.mark_done(task.id)

        # Assert：检查结果是不是符合预期。
        self.assertEqual(task.id, 1)
        self.assertTrue(completed.done)
        self.assertEqual(book.stats()["completed"], 1)

    def test_filter_by_tag_and_open_only(self):
        book = TaskBook()
        book.add("Learn lists", tags={"python", "basic"})
        done_task = book.add("Read JSON", tags={"file"})
        book.mark_done(done_task.id)

        python_tasks = book.visible_tasks(tag="python")
        open_tasks = book.visible_tasks(show_done=False)

        self.assertEqual([task.title for task in python_tasks], ["Learn lists"])
        self.assertEqual([task.title for task in open_tasks], ["Learn lists"])

    def test_missing_task_raises_error(self):
        book = TaskBook()

        # assertRaises 用来验证“这里应该抛出某种异常”。
        with self.assertRaises(TaskNotFoundError):
            book.find(404)

    def test_invalid_priority_raises_error(self):
        book = TaskBook()

        with self.assertRaises(InvalidPriorityError):
            book.add("Learn typing", priority="urgent")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
