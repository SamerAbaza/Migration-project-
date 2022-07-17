import datetime
from typing import Union

from pydantic import BaseModel


class PNotification(BaseModel):
    id: str
    status: str
    message: str
    submitted_date: Union[datetime.datetime, None]
    completed_date: Union[datetime.datetime, None]
    subject: str


class PConference(BaseModel):
    id: str
    name: str
    active: str
    date: datetime.date
    price: str
    address: str


class PAttendee(BaseModel):
    id: str
    first_name: str
    last_name: str
    conference_id: str
    job_position: str
    email: str
    company: str
    city: str
    state: str
    interests: str
    submitted_date: datetime.datetime
    comments: str