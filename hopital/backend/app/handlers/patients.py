
async def join_room(room_id, user_id, username, websocket, db):
    currRole = "client"
    if room_id not in rooms:
        fetched_data = await fetchRoom(room_id=room_id, db=db)
        lang = fetched_data["default_lang"]
        if lang is None:
            lang = "python"
            
        rooms[room_id] = Room(room_id, user_id, lang)
        currRole = "admin"
            
        
    room = rooms[room_id]
    
    if user_id in room.admins:
        currRole = "admin"

    # close old connection first
    if user_id in room.clients:
        try:
            await room.clients[user_id].close()
        except:
            pass

    await websocket.accept()
    room.clients[user_id] = websocket
    room.profile[user_id] = username

    room.code.setdefault(user_id, "")
    
    
    # await websocket.send_json(join_msg)
    
    initial_state = {
        "type": "room_state",
        "default_lang": room.default_lang,
        "users": [
            {
                "user_id": each_user_id,
                "role": "admin" if each_user_id in room.admins else "client",
                "display_name": room.profile.get(each_user_id, f"User {each_user_id}")
            }
            for each_user_id in room.clients.keys()
        ]
    }
    
    await websocket.send_json(initial_state)

    join_msg = message.user_joined(user_id=user_id, username=username, role=currRole, default_lang=room.default_lang)
    
    full_sync_data = message.full_sync(code=room.code, profiles=room.profile)
    # Full Sync
    await websocket.send_json(full_sync_data)
    # await websocket.send_json({
    #     "type": "full_sync",
    #     "code": room.code,
    #     "profile": room.profile
    # })
    
    # If user was disconnected, send back his own code
    existing_code = room.code.get(user_id, "")
    restore_data = Message.restore_code(user_id=user_id, code=existing_code)
    code_update_msg = Message.code_update(user_id=user_id, code=existing_code, stress_score=0)
    await websocket.send_json(restore_data)
    await websocket.send_json(code_update_msg)
    await broadcast(room=room, message=join_msg, target_user=None)

    return room
