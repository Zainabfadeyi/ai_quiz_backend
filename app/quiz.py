from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.post("/submit")
def submit_quiz(answers: dict, user=Depends(get_current_user)):
    return {
        "message": "Quiz submitted successfully",
        "submitted_by": user["username"],
        "answers": answers
    }
