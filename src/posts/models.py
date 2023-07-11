from src.database import Base
from src.auth.models import User

from sqlalchemy import ForeignKey, Column, TIMESTAMP, String, Integer, UUID, ForeignKeyConstraint

from datetime import datetime

class Post(Base):
    __tablename__ = "post"
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id']),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    head = Column(String(length=255), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    edit_at = Column(TIMESTAMP, default=datetime.utcnow)
    user_id = Column(UUID, nullable=False)