from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Project, ProjectBase, User
from security import oauth2_scheme, get_current_active_user


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[Project])
async def get_projects(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Project)
    else:
        statement = select(Project).filter(Project.owner_id == current_user.id)
    projects = session.exec(statement).all()
    return projects


@router.post("/", response_model=ProjectBase)
async def create_project(
    project: ProjectBase,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Project).filter(Project.name == project.name)
    else:
        statement = select(Project).filter(
            Project.name == project.name,
            Project.owner_id == current_user.id
        )
    project_exist = session.exec(statement).first()
    if project_exist:
        raise HTTPException(status_code=400, detail="Project already exists")
    project = Project(
        name=project.name,
        description=project.description,
        owner_id=current_user.id
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Project).filter(Project.id == project_id)
    else:
        statement = select(Project).filter(
            Project.id == project_id, Project.owner_id == current_user.id
        )
    project = session.exec(statement).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}")
async def update_project(
    project_id: int,
    project: ProjectBase,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Project).filter(Project.id == project_id)
    else:
        statement = select(Project).filter(
            Project.id == project_id, Project.owner_id == current_user.id
        )
    db_project = session.exec(statement).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_data = project.model_dump(exclude_unset=True)
    for key, value in project_data.items():
        setattr(db_project, key, value)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
):
    if current_user.is_superuser:
        statement = select(Project).filter(Project.id == project_id)
    else:
        statement = select(Project).filter(
            Project.id == project_id, Project.owner_id == current_user.id
        )
    project = session.exec(statement).first()
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    session.delete(project)
    session.commit()
    return {"ok": True}
