from fastapi import APIRouter, Request
from hopital.backend.app.utils.simulator import init

router = APIRouter(prefix="/simulations", tags=["simulations"])

@router.get("/init")
async def initalize():
    init()
    return {'init_success': True}

@router.get("/get_priority_score")
async def get_user(request: Request):
    return request.session.get("user")

@router.get("/profile")
async def fetchUserProfile():
    # user = await fetchUser(db=db, token=token)
    user = None
    return user