import uuid
import logging
from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatRequest, ChatResponse, FailSafeResponse, ComplianceOutputSchema
from ..services.compliance_engine import ComplianceEngine
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter()
compliance_engine = ComplianceEngine()
gemini_service = GeminiService()

@router.post("/api/chat")
async def process_chat(request: ChatRequest):
    try:
        if not request.message or len(request.message.strip()) == 0:
            return FailSafeResponse(
                status="under_review",
                message="Empty request detected. Please provide transaction details for analysis.",
                action_required=False
            ).dict()
        
        # Extract entities from message
        extracted = compliance_engine.extract_entities(request.message)
        
        # Run compliance checks if entities are available
        compliance_checks = []
        if extracted["transaction_id"] and extracted["amount"] > 0 and extracted["dispute_type"]:
            compliance_checks = compliance_engine.run_checks(
                extracted["transaction_id"],
                extracted["amount"],
                extracted["dispute_type"]
            )
        else:
            compliance_checks = [
                ComplianceOutputSchema(
                    rule_id="VRX_COMP_01",
                    rule_name="Transaction ID Validation",
                    status="PENDING",
                    audit_message="Awaiting transaction identifier"
                ),
                ComplianceOutputSchema(
                    rule_id="VRX_COMP_02",
                    rule_name="Amount Validation",
                    status="PENDING",
                    audit_message="Awaiting amount confirmation"
                ),
                ComplianceOutputSchema(
                    rule_id="VRX_COMP_03",
                    rule_name="Dispute Classification",
                    status="PENDING",
                    audit_message="Awaiting dispute classification"
                )
            ]
        
        # Get AI response
        ai_response = gemini_service.generate_response(
            request.message,
            request.role.value,
            extracted
        )
        
        # Merge compliance checks
        if compliance_checks:
            ai_response["compliance_checks"] = [c.dict() for c in compliance_checks]
        
        return ChatResponse(**ai_response)
        
    except Exception as e:
        logger.error(f"Unexpected error in chat route: {str(e)}")
        return FailSafeResponse().dict()

@router.get("/api/health")
async def health_check():
    return {"status": "operational", "service": "Verix AI Compliance Engine"}

@router.post("/api/validate")
async def validate_transaction(transaction_id: str, amount: float, dispute_type: str):
    try:
        checks = compliance_engine.run_checks(transaction_id, amount, dispute_type)
        all_passed = all(check.status == "PASSED" for check in checks)
        
        return {
            "valid": all_passed,
            "checks": [c.dict() for c in checks],
            "requires_review": not all_passed
        }
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return {"valid": False, "checks": [], "requires_review": True}