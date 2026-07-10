from datetime import datetime, date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db import Base


class HCP(Base):
    """A Healthcare Professional (doctor) the rep interacts with."""

    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    specialty = Column(String(200))
    organization = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship(
        "Interaction", back_populates="hcp", cascade="all, delete-orphan"
    )
    follow_ups = relationship(
        "FollowUp", back_populates="hcp", cascade="all, delete-orphan"
    )


class Interaction(Base):
    """A single logged interaction between a rep and an HCP."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    rep_name = Column(String(200))
    date = Column(Date, default=date.today)
    channel = Column(String(50))  # in-person / call / virtual
    product_discussed = Column(String(200))
    raw_notes = Column(Text)
    llm_summary = Column(Text)  # LLM-generated summary
    extracted_entities = Column(JSON)  # LLM-extracted structured entities
    sentiment = Column(String(50))  # positive / neutral / negative
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hcp = relationship("HCP", back_populates="interactions")
    follow_ups = relationship(
        "FollowUp", back_populates="interaction", cascade="all, delete-orphan"
    )


class FollowUp(Base):
    """A scheduled follow-up / next-best-action for an HCP."""

    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    due_date = Column(Date)
    action = Column(Text)
    status = Column(String(50), default="pending")  # pending / done / cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    hcp = relationship("HCP", back_populates="follow_ups")
    interaction = relationship("Interaction", back_populates="follow_ups")
