from fastapi import FastAPI
from app import auth, quiz, ai_feedback,models
from app.database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth.router)
app.include_router(quiz.router)
app.include_router(ai_feedback.router)

@app.get("/")
def root():
    return {"message": "Welcome to AI Quiz API"}
