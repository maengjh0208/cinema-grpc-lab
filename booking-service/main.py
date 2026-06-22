from fastapi import FastAPI
from routers.bookings import router as bookings_router
from routers.movies import router as movies_router

app = FastAPI()

app.include_router(movies_router)
app.include_router(bookings_router)


@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
