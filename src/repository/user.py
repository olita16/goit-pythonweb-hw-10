from sqlalchemy.orm import Session
from src.db.models import User
from src.schemas.auth import UserModel


async def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, db: Session):
    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def change_confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar_url(email: str, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user