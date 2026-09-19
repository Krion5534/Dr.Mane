from fastapi import APIRouter, Request, Depends
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/user", tags=["user"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

@router.get("/current")
async def get_user(request: Request):
    return request.session.get("user")

@router.get("/profile")
async def fetchUserProfile(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = await fetchUser(db=db, token=token)
    return user