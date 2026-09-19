class Message:
    
    @staticmethod
    def user_joined(user_id, username, role, default_lang):
        return {
            "type": "user_joined",
            "user_id": user_id,
            "role": role,
            "display_name": username,
            "default_lang": default_lang,
        }

    @staticmethod
    def user_left(user_id):
        return {
            "type": "user_left",
            "user_id": user_id
        }
    
    @staticmethod
    def user_kicked(user_id):
        return {
            "type": "user_kicked",
            "user_id": user_id
        }

    @staticmethod
    def code_update(user_id, code, stress_score=None):
        msg = {
            "type": "code_update",
            "user_id": user_id,
            "code": code
        }

        if stress_score is not None:
            msg["stress_score"] = stress_score

        return msg

    @staticmethod
    def full_sync(code, profiles):
        return {
            "type": "full_sync",
            "code": code,
            "profiles": profiles
        }

    @staticmethod
    def role_update(user_id, role):
        return {
            "type": "role_update",
            "user_id": user_id,
            "role": role
        }

    @staticmethod
    def error(message):
        return {
            "type": "error",
            "message": message
        }
        
    @staticmethod
    def restore_code(user_id, code):
        return {
            "type": "restore_code",
            "user_id": user_id,
            "code": code
        }
        
    @staticmethod
    def code_execution(result):
        return {
            "type": "code_execution",
            **result
        }
        