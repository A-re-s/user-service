from fastapi import APIRouter

from scripts.projects_router import projects_router
from scripts.scripts_router import scripts_router
from users.router import users_router


main_router = APIRouter(prefix="/api/v1")

main_router.include_router(users_router)
main_router.include_router(projects_router)
main_router.include_router(scripts_router)
