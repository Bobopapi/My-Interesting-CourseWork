from typing import Optional, Sequence, overload
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload
from ..models import Currency

@overload
def fetch(session: Session) -> Sequence[Currency]:
    ...

@overload
def fetch(session: Session, where: any) -> Sequence[Currency]:
    ...

def fetch(session: Session, where: Optional[any] = None) -> Sequence[Currency]:
    statement = select(Currency)

    if where is not None:
        statement = statement.where(where)
    
    return session.exec(statement).all()

def fetchById(session: Session, id: int) -> Optional[Currency]:
    return session.get(Currency, id)