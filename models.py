from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy import func
from database import Base

class ResearchRequest(Base):
    __tablename__ = 'research_requests'

    id = Column(String, primary_key=True, index=True)
    area_of_interest = Column(String, index=True, nullable=False)
    requested_by = Column(String, index=True, nullable=False)
    status = Column(String, index=True, nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)