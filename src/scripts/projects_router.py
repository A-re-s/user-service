from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from scripts.exceptions import already_exist, not_found
from scripts.models import ProjectModel
from scripts.schemas import ProjectInfoSchema, ProjectSchema
from users.dependencies import get_user_from_access_token
from users.schemas import UserSchema


projects_router = APIRouter()


@projects_router.post("/projects/", response_model=ProjectInfoSchema)
async def create_project(
    project: ProjectSchema,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProjectInfoSchema:

    new_project: ProjectModel = ProjectModel(name=project.name, owner_id=user.id)
    session.add(new_project)

    try:
        await session.commit()
        await session.refresh(new_project)
    except IntegrityError as exc:
        await session.rollback()
        raise already_exist("Project") from exc

    return new_project


@projects_router.get("/projects/", response_model=List[ProjectInfoSchema])
async def get_projects(
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> List[ProjectInfoSchema]:
    result = await session.execute(
        select(ProjectModel).where(ProjectModel.owner_id == user.id)
    )
    projects = result.scalars().all()
    return projects


@projects_router.get("/projects/{project_id}", response_model=ProjectInfoSchema)
async def get_project(
    project_id: int,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProjectInfoSchema:
    result = await session.execute(
        select(ProjectModel).where(
            ProjectModel.id == project_id, ProjectModel.owner_id == user.id
        )
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise not_found("Project")
    return project


@projects_router.put("/projects/{project_id}", response_model=ProjectInfoSchema)
async def update_project(
    project_id: int,
    updated_project: ProjectSchema,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProjectInfoSchema:
    result = await session.execute(
        select(ProjectModel).where(
            ProjectModel.id == project_id, ProjectModel.owner_id == user.id
        )
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise not_found("Project")

    project.name = updated_project.name

    try:
        await session.commit()
        await session.refresh(project)
    except IntegrityError as exc:
        await session.rollback()
        raise already_exist("Project") from exc

    return project


@projects_router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    result = await session.execute(
        select(ProjectModel).where(
            ProjectModel.id == project_id, ProjectModel.owner_id == user.id
        )
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise not_found("Project")

    await session.delete(project)
    await session.commit()
