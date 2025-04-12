"""Database models for the admission system."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Document(BaseModel):
    """Document model representing an uploaded document."""
    id: str
    file_name: str
    file_type: str
    file_path: str
    uploaded_at: datetime = Field(default_factory=datetime.now)
    verified: bool = False
    verification_notes: Optional[str] = None

class Student(BaseModel):
    """Student model representing a student in the system."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Program(BaseModel):
    """Program model representing an academic program."""
    id: str
    name: str
    department: str
    degree_level: str
    duration: str
    tuition_fee: float
    capacity: int
    description: Optional[str] = None

class Application(BaseModel):
    """Application model representing a student's application."""
    id: str
    student_id: str
    program_id: str
    status: str
    documents: Dict[str, str] = {}
    verification_notes: Optional[str] = None
    eligibility_score: Optional[float] = None
    shortlisting_notes: Optional[str] = None
    communications: List[Dict[str, Any]] = []
    loan_details: Optional[Dict[str, Any]] = None
    payment_details: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Communication(BaseModel):
    """Communication model representing a message sent to a student."""
    id: str
    application_id: str
    type: str
    subject: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sender: str
    status: str = "sent"

class Payment(BaseModel):
    """Payment model representing a fee payment."""
    id: str
    application_id: str
    amount: float
    payment_method: str
    payment_date: datetime = Field(default_factory=datetime.now)
    transaction_id: Optional[str] = None
    status: str = "pending"

class Loan(BaseModel):
    """Loan model representing a student loan."""
    id: str
    application_id: str
    amount: float
    interest_rate: float
    repayment_period_years: int
    status: str
    approval_date: Optional[datetime] = None
    approval_notes: Optional[str] = None