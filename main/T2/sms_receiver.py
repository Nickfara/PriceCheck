"""
todo Реализация перехвата СМС с кодом
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Хранилище последнего кода (опционально)
last_code = None


@app.get("/sms")
async def receive_sms(code: str):
    global last_code
    last_code = code
    print(f"[SMS CODE RECEIVED] Code: {code}")

    # Тут ты можешь вызывать другие функции, например:
    # process_2fa_code(code)

    return JSONResponse({"status": "ok", "code": code})


# Запуск сервера
if __name__ == "__main__":
    from requests import get

    ip = get('https://api.ipify.org').content.decode('utf8')
    print('Адрес сервера: {}'.format(ip))
    print()
    uvicorn.run("sms_receiver:app", host=str(ip), port=8000)
