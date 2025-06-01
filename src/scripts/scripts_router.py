from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from scripts.exceptions import already_exist, not_found
from scripts.models import ProjectModel, ScriptModel
from scripts.schemas import ScriptInfoSchema, ScriptSchema
from users.dependencies import get_user_from_access_token
from users.schemas import UserSchema


scripts_router = APIRouter()


@scripts_router.post("/projects/{project_id}/scripts", response_model=ScriptInfoSchema)
async def create_project(
    project_id: int,
    script: ScriptSchema,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScriptInfoSchema:

    result = await session.execute(
        select(ProjectModel).where(
            ProjectModel.id == project_id, ProjectModel.owner_id == user.id
        )
    )
    if result is None:
        raise not_found("Project")

    new_script: ScriptModel = ScriptModel(
        source_code=script.source_code, path=script.path, parent_project_id=project_id
    )
    session.add(new_script)

    try:
        await session.commit()
        await session.refresh(new_script)
    except IntegrityError as exc:
        await session.rollback()
        raise already_exist("Script") from exc

    return new_script


@scripts_router.get(
    "/projects/{project_id}/scripts", response_model=List[ScriptInfoSchema]
)
async def get_scripts(
    project_id: int,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> List[ScriptInfoSchema]:
    result = await session.execute(
        select(ScriptModel)
        .join(ProjectModel, ProjectModel.id == ScriptModel.parent_project_id)
        .where(ProjectModel.id == project_id, ProjectModel.owner_id == user.id)
    )
    scripts = result.scalars().all()
    return scripts


@scripts_router.get(
    "/projects/{project_id}/scripts/{script_id}", response_model=ScriptInfoSchema
)
async def get_script(
    project_id: int,
    script_id: int,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScriptInfoSchema:
    result = await session.execute(
        select(ScriptModel)
        .join(ProjectModel, ProjectModel.id == ScriptModel.parent_project_id)
        .where(
            ScriptModel.id == script_id,
            ProjectModel.id == project_id,
            ProjectModel.owner_id == user.id,
        )
    )
    script = result.scalar_one_or_none()
    if script is None:
        raise not_found("Script")
    return script


@scripts_router.put(
    "/projects/{project_id}/scripts/{script_id}", response_model=ScriptInfoSchema
)
async def update_script(
    project_id: int,
    script_id: int,
    updated_script: ScriptSchema,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ScriptInfoSchema:
    result = await session.execute(
        select(ScriptModel)
        .join(ProjectModel, ProjectModel.id == ScriptModel.parent_project_id)
        .where(
            ScriptModel.id == script_id,
            ProjectModel.id == project_id,
            ProjectModel.owner_id == user.id,
        )
    )
    script = result.scalar_one_or_none()
    if script is None:
        raise not_found("Script")

    script.path = updated_script.path
    script.source_code = updated_script.source_code

    try:
        await session.commit()
        await session.refresh(script)
    except IntegrityError as exc:
        await session.rollback()
        raise already_exist("Script") from exc

    return script


@scripts_router.delete("/projects/{project_id}/scripts/{script_id}", status_code=204)
async def delete_script(
    project_id: int,
    script_id: int,
    user: Annotated[UserSchema, Depends(get_user_from_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    result = await session.execute(
        select(ScriptModel)
        .join(ProjectModel, ProjectModel.id == ScriptModel.parent_project_id)
        .where(
            ScriptModel.id == script_id,
            ProjectModel.id == project_id,
            ProjectModel.owner_id == user.id,
        )
    )
    script = result.scalar_one_or_none()
    if script is None:
        raise not_found("Script")

    await session.delete(script)
    await session.commit()
