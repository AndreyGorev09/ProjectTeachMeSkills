from datetime import datetime
from typing import Optional

from delorean import Delorean
from django.db import models
from pydantic import BaseModel
from pydantic import Field




class Numbers(models.Model):
    name = models.TextField(unique=True)
    n = models.BigIntegerField(default=0)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name}, n={self.n})"

def utcnowtz() -> datetime:
    return Delorean().datetime


class Check(models.Model):
    name = models.TextField(blank=True, null=True)
    ip = models.TextField(blank=True, null=True)
    service = models.TextField(blank=True, null=True)
    at = models.DateTimeField(default=utcnowtz)
    ok = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    ms = models.IntegerField(blank=True, null=True)


class CheckT(BaseModel):
    id: Optional[int] = Field(None)
    name: str = Field(...)
    ip: Optional[str] = Field(None)
    service: str = Field(...)
    at: datetime = Field(default_factory=utcnowtz)
    ok: bool = Field(False)
    description: Optional[str] = Field(None)
    ms: int = Field(0)

    class Config:
        orm_mode = True