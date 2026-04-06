from pydantic import BaseModel, Field

class TranscriptRequest(BaseModel):
    transcript: str = Field(..., min_length=5)

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=2)