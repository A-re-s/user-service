from typing import Annotated

from pydantic import BaseModel, Field


class ScriptSchema(BaseModel):
    path: Annotated[str, Field(max_length=255)]
    source_code: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "path": "scripts/hello_world.py",
                    "source_code": "print('Hello, World!')",
                }
            ]
        }
    }


class ScriptInfoSchema(ScriptSchema):
    id: int
    parent_project_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "path": "scripts/hello_world.py",
                    "source_code": "print('Hello, World!')",
                    "parent_project_id": 42,
                }
            ]
        }
    }


class ProjectSchema(BaseModel):
    name: Annotated[str, Field(max_length=255)]

    model_config = {"json_schema_extra": {"examples": [{"name": "My First Project"}]}}


class ProjectInfoSchema(ProjectSchema):
    id: int
    owner_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 42, "name": "My First Project", "owner_id": 7}]
        }
    }
