import pytest
from pydantic import ValidationError

from app.schemas import TaskCreate


def test_task_accepts_title_with_surrounding_whitespace() -> None:
    task = TaskCreate(title="  Estudar CI  ")

    assert task.title == "  Estudar CI  "


@pytest.mark.parametrize("title", ["", "   "])
def test_task_rejects_empty_or_blank_title(title: str) -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title=title)


def test_task_rejects_title_longer_than_limit() -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title="x" * 121)
