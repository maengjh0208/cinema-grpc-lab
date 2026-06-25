from core.exception_handlers import register_exception_handlers
from fastapi import FastAPI
from routers.bookings import router as bookings_router
from routers.movies import router as movies_router

app = FastAPI()

# 순서 중요. include_router 전에 등록해야 함. FastAPI가 라우터 등록 시점에 핸들러를 연결하기 때문.
register_exception_handlers(app)

app.include_router(movies_router)
app.include_router(bookings_router)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
