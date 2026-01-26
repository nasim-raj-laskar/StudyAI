from typing import List
from pydantic import BaseModel, Field ,validator

class MCQQuestion(BaseModel):
    question:str=Field(description="The Question text")
    options:List[str]=Field(description="List of options for the MCQ")
    correct_option:int=Field(description="The correct option in the options list")
    
    @validator('question',pre=True)
    def clean_question(cls,v):
        if isinstance(v,str):
            return v.get('description',str(v))
        return str(v)
        
        
class FillBlankQuestion(BaseModel):
    question:str=Field(description="The Question text with '____' for the blank")
    answer:str=Field(description="The correct answer to fill in the blank")
    
    @validator('question',pre=True)
    def clean_question(cls,v):
        if isinstance(v,str):
            return v.get('description',str(v))
        return str(v)