"""
Coin transaction model for learning coin economy management
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class CoinTransaction(Base):
    """Learning coin transaction entity"""
    
    __tablename__ = "coin_transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to student
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    
    # Transaction details
    transaction_type = Column(String(20), nullable=False)  # earn, spend, refund, bonus
    amount = Column(Integer, nullable=False)  # Positive for earn, negative for spend
    balance_after = Column(Integer, nullable=False)
    
    # Transaction context
    source = Column(String(50), nullable=False)  # query_analysis, hint_purchase, achievement, etc
    source_reference_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to related entity
    description = Column(Text, nullable=True)
    
    # Metadata
    metadata = Column(String(500), nullable=True)  # Additional transaction context
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    student = relationship("Student", backref="coin_transactions")
    
    def __repr__(self):
        return f"<CoinTransaction(id={self.id}, student_id={self.student_id}, amount={self.amount})>" 