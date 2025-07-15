from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

Base = declarative_base()


# Enums for stable business concepts only (used in application logic)
class PriorityLevel(enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class SeniorityLevel(enum.Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """
    User model using Stack Auth user ID as primary key.

    Attributes:
        id: Stack Auth user ID as primary key
        role: User role (user, admin, super_admin)
        created_at: Account creation timestamp
        last_login: Last login timestamp
        companies: One-to-many relationship with Company
    """

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Stack Auth user ID
    role = Column(String(20), default=UserRole.USER.value)  # user, admin, super_admin
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # One user can have multiple companies (future-proofing)
    companies = relationship(
        "Company", back_populates="user", cascade="all, delete-orphan"
    )


class Company(Base):
    """
    Company model for storing analyzed company data.

    Stores all website analysis data in a single JSONB column for flexibility.
    Mirrors the TargetCompanyResponse structure from localStorage.
    """

    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Basic company information
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)

    # All analysis data stored as JSONB for flexibility
    data = Column(JSONB, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="companies")
    accounts = relationship(
        "Account", back_populates="company", cascade="all, delete-orphan"
    )


class Account(Base):
    """
    Account model for storing ideal customer profiles.

    Stores all account data in a single JSONB column for flexibility.
    Mirrors the AccountResponse structure from localStorage.
    """

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Basic account information
    name = Column(String(255), nullable=False)

    # All account data stored as JSONB for flexibility
    # Includes: firmographics, buyingSignals, rationale, metadata, etc.
    data = Column(JSONB, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="accounts")
    personas = relationship(
        "Persona", back_populates="account", cascade="all, delete-orphan"
    )
    campaigns = relationship(
        "Campaign", back_populates="account", cascade="all, delete-orphan"
    )


class Persona(Base):
    """
    Persona model for storing buyer personas.

    Stores all persona data in a single JSONB column for flexibility.
    Mirrors the PersonaResponse structure from localStorage.
    """

    __tablename__ = "personas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    # Basic persona information
    name = Column(String(255), nullable=False)

    # All persona data stored as JSONB for flexibility
    # Includes: demographics, useCases, buyingSignals, objections, goals, etc.
    data = Column(JSONB, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="personas")
    campaigns = relationship(
        "Campaign", back_populates="persona", cascade="all, delete-orphan"
    )


class Campaign(Base):
    """
    Campaign model for storing generated marketing campaigns.

    Stores all campaign data in a single JSONB column for flexibility.
    Supports emails, LinkedIn, cold calls, ads, etc.
    """

    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)

    # Basic campaign information
    name = Column(String(255), nullable=False)
    type = Column(
        String(50), nullable=False
    )  # flexible: email, linkedin, cold_call, ad

    # All campaign data stored as JSONB for flexibility
    # Includes: subject_line, content, segments, alternatives, configuration, etc.
    data = Column(JSONB, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="campaigns")
    persona = relationship("Persona", back_populates="campaigns")
