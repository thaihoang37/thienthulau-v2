from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy import event


class BaseModelWithTimestamp(SQLModel):
    created_date: datetime = Field(default_factory=datetime.utcnow)
    updated_date: datetime = Field(default_factory=datetime.utcnow)


@event.listens_for(BaseModelWithTimestamp, "before_update", propagate=True)
def update_timestamp(mapper, connection, target):
    target.updated_date = datetime.utcnow()
