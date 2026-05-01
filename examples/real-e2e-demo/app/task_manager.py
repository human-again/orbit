class TaskManager:
    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def add_task(self, title, priority="medium"):
        tid = self._next_id
        self._tasks[tid] = {"id": tid, "title": title, "priority": priority, "done": False}
        self._next_id += 1
        return tid

    def get_task(self, task_id):
        return self._tasks.get(task_id)

    def mark_done(self, task_id):
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task["done"] = True
        return True

    def filter_by_priority(self, priority):
        return [t for t in self._tasks.values() if t["priority"] == priority]

    def summary(self):
        tasks = list(self._tasks.values())
        done = sum(1 for t in tasks if t["done"])
        return {"total": len(tasks), "done": done, "pending": len(tasks) - done}
