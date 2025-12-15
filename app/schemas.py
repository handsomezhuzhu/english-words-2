from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    preferred_language: str = "en"
    preferred_theme: str = "light"


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    is_admin: Optional[bool] = None



class WordBase(BaseModel):
    english: Optional[str] = None
    chinese: Optional[str] = None
    phonetics: Optional[str] = None  # JSON string
    definition: Optional[str] = None
    part_of_speech: Optional[str] = None
    parts_of_speech: Optional[str] = None  # JSON string
    examples: Optional[str] = None  # JSON string


class WordCreate(WordBase):
    pass


class Word(WordBase):
    id: int
    next_review_at: datetime
    interval_index: int
    success_streak: int

    class Config:
        from_attributes = True


class SystemConfigBase(BaseModel):
    provider: str = "openai"
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: int = 0


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfig(SystemConfigBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    count: int
    mode: str  # en_to_zh or zh_to_en


class ReviewItem(BaseModel):
    id: int
    question: str
    answer: str


class ReviewAnswer(BaseModel):
    grade: int  # 0: Don't know, 1: Unclear, 2: Know


class AICompletionRequest(BaseModel):
    word: str
    direction: str = "en_to_zh"


class Phonetics(BaseModel):
    uk: Optional[str] = None
    us: Optional[str] = None


class PartOfSpeech(BaseModel):
    pos: str
    meaningEn: Optional[str] = None
    meaningZh: Optional[str] = None


class Example(BaseModel):
    sentenceEn: str
    sentenceZh: str


class AICompletionResponse(BaseModel):
    word: str
    phonetics: Optional[Phonetics] = None
    partsOfSpeech: List[PartOfSpeech] = []
    examples: List[Example] = []
    synonyms: List[str] = []
    antonyms: List[str] = []
    direction: str
