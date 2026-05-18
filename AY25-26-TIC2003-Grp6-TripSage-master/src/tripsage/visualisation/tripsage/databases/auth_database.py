from typing import Optional, Sequence, overload
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from ..models import Auth

def fetchById(session: Session, id: int) -> Optional[Auth]:
    return session.exec(
        select(Auth)
        .where(Auth.id == id)
    ).first()

def fetchByEmail(session: Session, email: str) -> Optional[Auth]:
    return session.exec(
        select(Auth)
        .where(Auth.email == email)
    ).first()

def insert(session: Session, model: Auth):
    session.add(model)