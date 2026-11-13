import os
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base, Task
from app.schemas import TaskCreate, TaskRead, TaskUpdate

DEFAULT_DATABASE_URL = "postgresql+psycopg://tasks:tasks@localhost:5432/tasks"


def create_app(database_url: str | None = None) -> FastAPI:
    """Create the API and its database connection."""
    resolved_database_url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    engine = create_engine(resolved_database_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    app = FastAPI(
        title="Tasks API",
        description="API REST para cadastro e acompanhamento de tarefas.",
        version="1.0.0",
    )

    @app.on_event("startup")
    def create_tables() -> None:
        Base.metadata.create_all(bind=engine)

    def get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
    def create_task(
        payload: TaskCreate, session: Annotated[Session, Depends(get_session)]
    ) -> Task:
        task = Task(title=payload.title.strip(), description=payload.description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @app.get("/tasks", response_model=list[TaskRead])
    def list_tasks(session: Annotated[Session, Depends(get_session)]) -> list[Task]:
        return list(session.scalars(select(Task).order_by(Task.id)))

    @app.get("/tasks/{task_id}", response_model=TaskRead)
    def get_task(
        task_id: int, session: Annotated[Session, Depends(get_session)]
    ) -> Task:
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        return task

    @app.patch("/tasks/{task_id}", response_model=TaskRead)
    def update_task(
        task_id: int,
        payload: TaskUpdate,
        session: Annotated[Session, Depends(get_session)],
    ) -> Task:
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value.strip() if field == "title" else value)
        session.commit()
        session.refresh(task)
        return task

    @app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_task(
        task_id: int, session: Annotated[Session, Depends(get_session)]
    ) -> None:
        task = session.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        session.delete(task)
        session.commit()

    return app


app = create_app()
