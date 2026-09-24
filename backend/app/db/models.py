from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.app.db.database import Base

class UserRole(str, enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

class AgeGroup(str, enum.Enum):
    UNDER_14 = "UNDER_14"
    AGE_14_TO_17 = "AGE_14_TO_17"
    AGE_18_PLUS = "AGE_18_PLUS"

class SafetyClassification(str, enum.Enum):
    SAFE_FOR_ALL = "SAFE_FOR_ALL"
    SAFE_14_PLUS = "SAFE_14_PLUS"
    SAFE_18_PLUS = "SAFE_18_PLUS"
    UNSAFE_FOR_ALL = "UNSAFE_FOR_ALL"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"

class ModerationAction(str, enum.Enum):
    APPROVE = "APPROVE"
    AGE_RESTRICT = "AGE_RESTRICT"
    REJECT = "REJECT"
    HUMAN_REVIEW = "HUMAN_REVIEW"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    
    age_verification_status = Column(String(50), default="VERIFIED")
    verified_age_group = Column(SQLEnum(AgeGroup), nullable=True)
    estimated_age = Column(Float, nullable=True)
    chronological_age = Column(Integer, nullable=True)
    age_difference = Column(Float, nullable=True)
    age_confidence = Column(Float, default=0.95)
    
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    advertisements = relationship("Advertisement", back_populates="owner")
    audit_logs = relationship("AuditLog", back_populates="user")

class Advertisement(Base):
    __tablename__ = "advertisements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    caption = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=False)
    media_type = Column(String(50), default="image")
    status = Column(String(50), default="PENDING")
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="advertisements")
    moderation_result = relationship("ModerationResult", back_populates="advertisement", uselist=False)

class ModerationResult(Base):
    __tablename__ = "moderation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    advertisement_id = Column(Integer, ForeignKey("advertisements.id"), unique=True)
    model_version = Column(String(100), default="SafeAd_V2_Multimodal")
    
    classification = Column(SQLEnum(SafetyClassification), nullable=False)
    risk_category = Column(String(100), nullable=False)
    risk_score = Column(Float, nullable=True)
    confidence = Column(Float, default=0.85)
    explanation = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)  # Detailed JSON assessment matrix string
    
    moderation_action = Column(SQLEnum(ModerationAction), nullable=False)
    age_restriction = Column(Integer, nullable=True)
    publishable = Column(Boolean, default=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Human-in-the-Loop fields
    is_human_reviewed = Column(Boolean, default=False)
    moderator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderator_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), default=func.now())
    
    advertisement = relationship("Advertisement", back_populates="moderation_result")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("advertisements.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="audit_logs")
