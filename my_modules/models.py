from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Relationship, Field 

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password: str
    schedules: List["Schedule"] = Relationship(back_populates="owner")
    profile: Optional["Profile"] = Relationship(back_populates="user", sa_relationship_kwargs=dict(uselist=False))
    

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None)
    email: str
    username: Optional[str] = Field(default=None)
    occupation: Optional[str] = Field(default=None)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="profile")


class Schedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    date_created: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[int] = Field(default = None, foreign_key="user.id")
    owner: User = Relationship(back_populates="schedules")
    activities: List["Activity"] = Relationship(back_populates="schedule")


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    time: datetime
    repetitive: bool = Field(default=False)
    completed: bool = Field(default=False)
    schedule_id: Optional[int] = Field(default=None, foreign_key="schedule.id")
    schedule: Schedule = Relationship(back_populates="activities")
