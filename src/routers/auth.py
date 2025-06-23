from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.db.connect import get_db
from src.schemas.auth import User, UserModelRegister, UserModel
from src.repository.auth import (
    Hash,
    create_access_token,
    get_email_from_token,
)
from src.repository.user import create_user, get_user_by_email, change_confirmed_email
from src.services.email import send_email
from src.services.auth import auth_service
from src.services.limiter import limiter


router = APIRouter(prefix="/auth", tags=["auth"])

hash_handler = Hash()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserModelRegister,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    user = await get_user_by_email(body.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = hash_handler.get_password_hash(body.password)
    new_user = await create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.first_name, str(request.base_url)
    )
    return new_user


@router.post("/login", status_code=status.HTTP_201_CREATED)
async def login(body: UserModel, db: Session = Depends(get_db)):
    user = await get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )

    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )

    access_token = await create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await get_email_from_token(token)

    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await change_confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.get("/me")
@limiter.limit("5/minute")
async def get_current_user_info(
    request: Request, user: User = Depends(auth_service.get_current_user)
):
    return {"email": user.email, "id": user.id, "confirmed": user.confirmed}