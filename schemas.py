from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RegisterIn(Strict):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=10, max_length=128)


class LoginIn(Strict):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class ConsentIn(Strict):
    kind: Literal["profile", "document_use"]
    granted: bool


class ProfileIn(Strict):
    """Data minimisation: only what eligibility rules need."""
    language: str = Field(default="en", pattern=r"^[a-z]{2,3}(-[A-Za-z]{2,4})?$")
    state: Optional[str] = Field(default=None, max_length=40)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    annual_income: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=10)
    occupation: Optional[str] = Field(default=None, max_length=40)
    gender: Optional[str] = Field(default=None, max_length=20)
    land_holding_hectares: Optional[float] = Field(default=None, ge=0)
    is_student: Optional[bool] = None

    @field_validator("category", "occupation", "state")
    @classmethod
    def upper(cls, v):
        return v.strip().upper() if v else v


class ChatIn(Strict):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en", max_length=10)


class ApplicationIn(Strict):
    scheme_id: str = Field(max_length=64)


class FormPatchIn(Strict):
    fields: dict = Field(max_length=20)


class ConfirmIn(Strict):
    confirm: bool


class SubmitIn(Strict):
    approval_token: str = Field(max_length=2000)
    confirm: bool


class StatusIn(Strict):
    status: Literal["received", "under_review", "query_raised", "approved", "rejected", "other"]
    note: Optional[str] = Field(default=None, max_length=300)


class PinIn(Strict):
    pin: str = Field(pattern=r"^\d{4,8}$")


class ConfirmFieldIn(Strict):
    field: str = Field(max_length=30)
    value: str = Field(min_length=1, max_length=100)


class ProfileAnswerIn(Strict):
    field: str = Field(max_length=30)
    answer: str = Field(min_length=1, max_length=200)


class IngestIn(Strict):
    source_url: str = Field(max_length=300)
    text: str = Field(min_length=20, max_length=20000)
    pack: str = Field(max_length=40)
    scheme_id: str = Field(pattern=r"^[a-z0-9-]{3,64}$")


class ReviewNoteIn(Strict):
    note: Optional[str] = Field(default=None, max_length=300)


class SpeakIn(Strict):
    text: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en", max_length=10)
