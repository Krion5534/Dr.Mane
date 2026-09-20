from fastapi import APIRouter, Request, Query, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException


router = APIRouter(prefix="/paients", tags=["patients"])
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")




@router.get("/admit")
async def createRoom(
    lang: str,
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):    
    
    user = await fetchUser(token=token, db=db)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    room = Room(
        default_lang = lang,
        created_by = user["id"]
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return {"code": room.id}
    
        

@router.websocket("/view/all")
async def websocket(
    websocket: WebSocket,
    token: str | None = None
):
    
    if not token:
        await websocket.close(1000)
        return
    
    user = await fetchUser(token=token, db=db)
    
    room = await join_room(room_id=room_code, user_id=user["id"], username=user["display_name"], websocket=websocket, db=db)

    fetchPatients()

    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "code_change":
                content = data.get("code")
                if (room.code.get(user["id"]) == content):
                    continue
                await update_code(room_id=room_code, user_id=user["id"], code=content)
                msg = Message.code_update(
                    user_id=user["id"],
                    code=content,
                    stress_score=0.00
                )
                await broadcast(room=room, message=msg, target="admins")
                
            elif message_type == "code_execution":
                code = data.get("code")
                lang = data.get("default_lang")
                inputs = data.get("inputs", [])
                
                stdin = "\n".join(inputs)
                        
                res = await executeCode(code=code, language=lang, stdin=stdin)
                
                msg = Message.code_execution(result=res)
                
                await broadcast(message=msg, room=room, target_user=user["id"])
                
            elif message_type == "kick_user":
                user_to_be_kicked = data.get("user_id")
                if room.isAdmin(user["id"]):
                    await room.kickUser(user_to_be_kicked)
                    msg = Message.user_kicked(user_id=user_to_be_kicked)
                    await broadcast(message=msg, room=room, target="all")
            print(data)
            
    except WebSocketDisconnect:
        leave_room(room_code=room_code, user_id=user["id"])
        msg = Message.user_left(user_id=user["id"])
        await broadcast(room=room, message=msg)
        print(f"{user['display_name']} left {room_code}")