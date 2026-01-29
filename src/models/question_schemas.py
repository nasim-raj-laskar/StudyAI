from typing import List
from pydantic import BaseModel, Field

class MCQQuestion(BaseModel):
    question: str = Field(description="The Question text")
    options: List[str] = Field(description="List of exactly 4 options for the MCQ")
    correct_answer: str = Field(description="The correct answer from the options")


class FillBlankQuestion(BaseModel):
    question: str = Field(description="The Question text with '_____' for the blank")
    answer: str = Field(description="The correct answer to fill in the blank")