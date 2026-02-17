from typing import List
from pydantic import BaseModel, Field

class Flashcard(BaseModel):
    front: str = Field(description="The question or concept on the front of the flashcard")
    back: str = Field(description="The answer or explanation on the back of the flashcard")

class FlashcardSet(BaseModel):
    flashcards: List[Flashcard] = Field(description="A collection of study flashcards")
