from typing import Annotated

from pydantic import BaseModel, Field


class ScriptSchema(BaseModel):
    path: Annotated[str, Field(max_length=255)]
    source_code: str


class ScriptInfoSchema(ScriptSchema):
    id: int
    parent_project_id: int


class ProjectSchema(BaseModel):
    name: Annotated[str, Field(max_length=255)]


class ProjectInfoSchema(ProjectSchema):
    id: int
    owner_id: int
