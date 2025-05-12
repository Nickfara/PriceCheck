from T2.api import T2Api
from functions import t2b
import threading
from log import log

_sessions = {}
_lock = threading.Lock()

def get_api(uid: int) -> T2Api:
    """
    Возвращает экземпляр T2Api для пользователя. Если нет — создаёт.
    """
    with _lock:
        if uid in _sessions:
            return _sessions[uid]

        DB = t2b(uid)
        if not DB or "auth_login" not in DB:
            raise ValueError(f"Пользователь {uid} не найден или не авторизован!")

        phone = DB["auth_login"]
        token = DB.get("token", "")
        refresh_token = DB.get("refresh_token", "")
        api = T2Api(phone, access_token=token, refresh_token=refresh_token)

        if DB['stage_authorize'] == 3:
            if not api.check_if_authorized():
                log(f"Пользователь {uid} не авторизован — сбрасываю сессию", 2)
                reset_api(uid)
                raise ValueError("Сессия недействительна")

        _sessions[uid] = api
        return api

def reset_api(uid: int):
    """
    Сбрасывает экземпляр API, например при сбросе токенов
    """
    with _lock:
        if uid in _sessions:
            del _sessions[uid]