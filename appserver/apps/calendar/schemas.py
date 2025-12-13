from typing import Annotated
from sqlmodel import SQLModel, Field
from pydantic import AwareDatetime, EmailStr, AfterValidator
from appserver.libs.collections.sort import deduplicate_and_sort
from datetime import time
from pydantic import model_validator as model_valid

class CalendarOut(SQLModel):
    topics: list[str]
    description: str

class CalendarDetailOut(CalendarOut):
    host_id: int
    google_calendar_id: str
    created_at: AwareDatetime
    updated_at: AwareDatetime

Topics = Annotated[list[str], AfterValidator(deduplicate_and_sort)]
class CalendarCreateIn(SQLModel):
    topics: Topics = Field(min_length=1, description="게스트와 나눌 주제들")
    description: str = Field(min_length=1, description="게스트에게 보여 줄 설명")
    google_calendar_id: str = Field(description="Google Calendar ID")

class CalendarUpdateIn(SQLModel):
    topics: Topics | None = Field(default=None, min_length=1, description=">게스트와 나눌 주제들>",)
    description: str | None = Field(default=None, min_length=10, description=">게스트에게 보여 줄 설명>")
    google_calendar_id: str | None = Field(default=None, min_length=20, description="Google Calendar ID")

def validate_weekdays(weekdays: list[int]) -> list[int]:
    weekday_range = range(7)
    for weekday in weekdays:
        if weekday not in weekday_range:
            raise ValueError("weekdays must be between 0 and 6")
    return weekdays

Weekdays = Annotated[list[int], AfterValidator(validate_weekdays)]

class TimeSlotCreateIn(SQLModel):
    start_time: time
    end_time: time
    weekdays: list[int]
    @model_valid(mode="after")
    def validate_time_slot(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be less than end_time")
        return self

class TimeSlotOut(SQLModel):
    start_time: time
    end_time: time
    weekdays: list[int]
    created_at: AwareDatetime
    updated_at: AwareDatetime