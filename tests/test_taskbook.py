import unittest

from python_study_start.models import InvalidPriorityError, TaskBook, TaskNotFoundError


class TaskBookTest(unittest.TestCase):
    def test_add_and_complete_task(self):
        book = TaskBook()

        task = book.add("Learn functions", priority="high", tags={"python"})
        completed = book.mark_done(task.id)

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

        with self.assertRaises(TaskNotFoundError):
            book.find(404)

    def test_invalid_priority_raises_error(self):
        book = TaskBook()

        with self.assertRaises(InvalidPriorityError):
            book.add("Learn typing", priority="urgent")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

