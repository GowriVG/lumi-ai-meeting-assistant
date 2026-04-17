from pydantic import BaseModel, Field, validator

class TranscriptRequest(BaseModel):
    transcript: str

    @validator("transcript")
    def validate_transcript(cls, v):
        if not v.strip():
            raise ValueError("Transcript cannot be empty")
        return v

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=2)