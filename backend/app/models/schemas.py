from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    CONSUMER = "consumer"
    VENDOR = "vendor"

class DisputeType(str, Enum):
    DOUBLE_DEDUCTION = "double_deduction"
    INVOICE_MISMATCH = "invoice_mismatch"
    REFUND_PENDING = "refund_pending"

class UserSessionSchema(BaseModel):
    user_id: UUID
    email: str
    role: UserRole
    company_name: Optional[str] = None

class DisputePayloadSchema(BaseModel):
    transaction_id: str
    amount: float
    dispute_type: DisputeType
    user_raw_input: str
    
    @validator('user_raw_input')
    def validate_input_length(cls, v):
        if len(v) > 5000:
            raise ValueError('Input exceeds maximum length of 5000 characters')
        if not v.strip():
            raise ValueError('Input cannot be empty')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v

class ComplianceOutputSchema(BaseModel):
    rule_id: str
    rule_name: str
    status: str
    audit_message: str

class ChatRequest(BaseModel):
    message: str
    role: UserRole
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversational_response: str
    action_triggered: bool
    extracted_entities: dict
    compliance_checks: List[ComplianceOutputSchema]
    system_status_update: str

class FailSafeResponse(BaseModel):
    status: str = "under_review"
    message: str = "The request is temporarily being reviewed due to incomplete or unverified transaction data."
    action_required: bool = False