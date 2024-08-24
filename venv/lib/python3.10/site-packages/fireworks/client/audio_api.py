from typing import List, Optional
from pydantic import BaseModel, Field


class Error(BaseModel, extra="forbid"):
    object: str = "error"
    type: str = "invalid_request_error"
    message: str


class ErrorResponse(BaseModel, extra="forbid"):
    error: Error = Field(default_factory=Error)


class TranscriptionRequest(BaseModel, extra="forbid"):
    # file: int
    model: str
    language: Optional[str]
    prompt: Optional[str]
    response_format: Optional[str]
    temperature: Optional[float]
    timestamp_granularities: Optional[List[str]]


class TranscriptionResponse(BaseModel, extra="forbid"):
    text: str


class TranscriptionWord(BaseModel, extra="forbid"):
    word: str
    start: float
    end: float


class TranscriptionSegment(BaseModel, extra="forbid"):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class TranscriptionVerboseResponse(BaseModel, extra="forbid"):
    task: str = "transcribe"  # Not documented by returned by OAI API
    language: str
    duration: float
    text: str
    words: Optional[List[TranscriptionWord]] = None
    segments: Optional[List[TranscriptionSegment]] = None


class TranslationRequest(BaseModel, extra="forbid"):
    # file: int
    model: str
    prompt: Optional[str]
    response_format: Optional[str]
    temperature: Optional[float]
