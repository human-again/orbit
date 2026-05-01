import pytest
from task_manager import TaskManager


@pytest.fixture
def tm():
    return TaskManager()


# --- mark_done tests (task-001) ---

def test_mark_done_returns_true(tm):
    tid = tm.add_task("Write tests", priority="high")
    assert tm.mark_done(tid) is True


def test_mark_done_sets_done_flag(tm):
    tid = tm.add_task("Write tests", priority="high")
    tm.mark_done(tid)
    assert tm.get_task(tid)["done"] is True


def test_mark_done_missing_id_returns_false(tm):
    assert tm.mark_done(999) is False


# --- filter_by_priority tests (task-002) ---

def test_filter_by_priority_returns_matching(tm):
    tm.add_task("High task", priority="high")
    tm.add_task("Medium task", priority="medium")
    tm.add_task("Another high", priority="high")
    results = tm.filter_by_priority("high")
    assert len(results) == 2
    assert all(t["priority"] == "high" for t in results)


def test_filter_by_priority_empty_when_none_match(tm):
    tm.add_task("Medium task", priority="medium")
    assert tm.filter_by_priority("low") == []


def test_filter_by_priority_all_tasks_if_all_match(tm):
    tm.add_task("A", priority="low")
    tm.add_task("B", priority="low")
    results = tm.filter_by_priority("low")
    assert len(results) == 2


# --- summary tests (task-003) ---

def test_summary_empty(tm):
    result = tm.summary()
    assert result == {"total": 0, "done": 0, "pending": 0}


def test_summary_all_pending(tm):
    tm.add_task("A")
    tm.add_task("B")
    result = tm.summary()
    assert result == {"total": 2, "done": 0, "pending": 2}


def test_summary_mixed(tm):
    t1 = tm.add_task("A")
    tm.add_task("B")
    tm.mark_done(t1)
    result = tm.summary()
    assert result == {"total": 2, "done": 1, "pending": 1}


def test_summary_all_done(tm):
    t1 = tm.add_task("A")
    t2 = tm.add_task("B")
    tm.mark_done(t1)
    tm.mark_done(t2)
    result = tm.summary()
    assert result == {"total": 2, "done": 2, "pending": 0}
