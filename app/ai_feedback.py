from fastapi import APIRouter, Depends
from app.auth import get_current_user
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(prefix="/ai", tags=["AI"])

# class FeedbackRequest(BaseModel):
#     answers: Dict[str, str]
class QuestionItem(BaseModel):
    question: str
    correct_answer: str
    student_answer: str

class FeedbackRequest(BaseModel):
    answers: Dict[str, QuestionItem]

@router.post("/feedback")
def get_feedback(data: FeedbackRequest, current_user=Depends(get_current_user)):
    try:
        # model = genai.GenerativeModel("gemini-pro")
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        # prompt = f"Review the student's quiz answers and provide constructive feedback:\n\n{data.answers}"
        prompt_parts = ["Review the student's quiz answers and provide feedback:\n"]

        for qid, qdata in data.answers.items():
            prompt_parts.append(f"""
        Question: {qdata.question}
        Correct Answer: {qdata.correct_answer}
        Student Answer: {qdata.student_answer}
        """)

        prompt = "\n".join(prompt_parts)

        response = model.generate_content(prompt)

        return {"feedback": response.text}
    except Exception as e:
        return {"error": str(e)}
    
# for model in genai.list_models():
#     print(model.name, model.supported_generation_methods)

