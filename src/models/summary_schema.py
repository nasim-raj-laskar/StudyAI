from typing import List
from pydantic import BaseModel, Field

class SummarySchema(BaseModel):
    main_idea: str = Field(description="The core message or central theme of the content")
    key_points: List[str] = Field(description="List of the most important takeaways and details")
