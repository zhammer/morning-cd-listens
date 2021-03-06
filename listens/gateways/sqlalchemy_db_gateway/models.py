from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from listens.definitions import MusicProvider


Base: Any = declarative_base()


class SqlListen(Base):
    __tablename__ = 'listens'

    id = Column(Integer(), primary_key=True)
    song_id = Column(String(50), nullable=False)
    song_vendor = Column(Enum(MusicProvider), nullable=False)  # TODO: Change to song_provider.
    listener_name = Column(String(30), nullable=False)
    note = Column(String(100), nullable=True)
    listen_time_utc = Column(DateTime(), nullable=False, index=True)
    iana_timezone = Column(String(40), nullable=False)
    created_at_utc = Column(DateTime(), nullable=False, default=datetime.utcnow)
    updated_on_utc = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
