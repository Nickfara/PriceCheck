from T2.api import T2Api

_api_instance = None

def get_api(*args, **kwargs):
    global _api_instance
    if _api_instance is None:
        _api_instance = T2Api(*args, **kwargs)
    return _api_instance