import pickle
import redis

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from src.repository.user import get_user_by_email
from src.db.connect import get_db
from sqlalchemy.orm import Session


from src.settings.base import ALGORITHM, SECRET_KEY


class Auth:

    r = redis.Redis(host="redis", port=6379, db=0)

    async def get_current_user(
        self,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: Session = Depends(get_db),
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            print("Payload from token:", payload)
            email = payload["sub"]
            if email is None:
                print("No sub in token")
                raise credentials_exception
        except JWTError as e:
            print("JWT error:", e)
            raise credentials_exception

        user = self.r.get(f"user:{email}")

        if user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        if user is None:
            raise credentials_exception
        return user


auth_service = Auth()