from fastapi import FastAPI
from app.api import (
    user, psychologist, specialization, appointment,
    chat, schedule, review
)

app = FastAPI()

app.include_router(user.router)
app.include_router(psychologist.router)
app.include_router(specialization.router)
app.include_router(appointment.router)
app.include_router(chat.router)
app.include_router(schedule.router)
app.include_router(review.router)
