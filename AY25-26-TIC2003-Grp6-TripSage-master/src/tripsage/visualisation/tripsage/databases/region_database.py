from typing import Optional, Sequence, overload
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from ..models import Region

@overload
def fetch(session: Session) -> Sequence[Region]:
    ...

@overload
def fetch(session: Session, where: any) -> Sequence[Region]:
    ...

def fetch(session: Session, where: Optional[any] = None) -> Sequence[Region]:
    statement = select(Region).options(joinedload(Region.country))

    if where is not None:
        statement = statement.where(where)
    
    return session.exec(statement).all()

def fetchById(session: Session, id: int) -> Optional[Region]:
    return session.exec(
        select(Region)
        .where(Region.id == id)
        .options(joinedload(Region.country))
    ).first()