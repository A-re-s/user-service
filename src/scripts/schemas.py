from pydantic import BaseModel, Field


class ScriptSchema(BaseModel):
    path: str = Field(max_length=255)
    parent_project_id: int
    source_code: str


class ProjectSchema(BaseModel):
    name: str = Field(max_length=255)
    owner_id: int
