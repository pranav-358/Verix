import json
import logging
from typing import Dict, Any
import google.generativeai as genai
from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    
    def __init__(self):
        self.is_available = False
        if config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.is_available = True
                logger.info("Gemini service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
        else:
            logger.warning("GEMINI_API_KEY not found, running in deterministic mode")
    
    def generate_response(self, user_input: str, role: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_available:
            return self._get_fallback_response(user_input, role, extracted_data)
        
        try:
            system_prompt = self._build_system_prompt(role, extracted_data)
            full_prompt = f"{system_prompt}\n\nUser input: {user_input}"
            
            response = self.model.generate_content(full_prompt)
            raw_response = response.text.strip()
            
            # Extract JSON from response
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                return json.loads(json_str)
            else:
                return self._get_fallback_response(user_input, role, extracted_data)
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return self._get_fallback_response(user_input, role, extracted_data)
    
    def _build_system_prompt(self, role: str, extracted_data: Dict[str, Any]) -> str:
        base_prompt = """You are Verix AI, a Financial Dispute Intelligence Engine. Respond with ONLY valid JSON. No markdown, no explanations, no headers.

Output format:
{"conversational_response": "string", "action_triggered": true, "extracted_entities": {"transaction_id": "string_or_null", "amount": 0.0, "dispute_type": "string_or_null"}, "compliance_checks": [{"rule_id": "string", "rule_name": "string", "status": "PASSED/FAILED/PENDING", "audit_message": "string"}], "system_status_update": "open/under_review"}"""
        
        if role == "consumer":
            role_context = """
Role: Consumer Support
Focus: Transaction anomalies, double deductions, refund delays
Tone: Empathetic but precise, operational clarity"""
        else:
            role_context = """
Role: Vendor Compliance
Focus: Invoice reconciliation, payment mismatches, audit irregularities
Tone: Strict financial auditing, highlight inconsistencies clearly"""
        
        extracted_info = f"\nExtracted data: {json.dumps(extracted_data)}"
        
        return base_prompt + role_context + extracted_info
    
    def _get_fallback_response(self, user_input: str, role: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        has_data = extracted_data.get("transaction_id") and extracted_data.get("amount") > 0
        dispute_type = extracted_data.get("dispute_type")
        
        if has_data and dispute_type:
            if role == "consumer":
                response_text = f"We've identified a {dispute_type.replace('_', ' ')} related to transaction {extracted_data['transaction_id']} for ${extracted_data['amount']:.2f}. Our compliance team is reviewing this matter."
            else:
                response_text = f"Compliance alert: {dispute_type.replace('_', ' ')} detected for transaction {extracted_data['transaction_id']} amounting to ${extracted_data['amount']:.2f}. Further audit required."
            
            return {
                "conversational_response": response_text,
                "action_triggered": True,
                "extracted_entities": extracted_data,
                "compliance_checks": [
                    {
                        "rule_id": "VRX_COMP_01",
                        "rule_name": "Transaction ID Validation",
                        "status": "PASSED" if extracted_data["transaction_id"] else "PENDING",
                        "audit_message": "Transaction identifier present" if extracted_data["transaction_id"] else "Awaiting transaction reference"
                    },
                    {
                        "rule_id": "VRX_COMP_02",
                        "rule_name": "Amount Validation",
                        "status": "PASSED" if extracted_data["amount"] > 0 else "PENDING",
                        "audit_message": f"Amount ${extracted_data['amount']:.2f} under review" if extracted_data["amount"] > 0 else "Amount not specified"
                    },
                    {
                        "rule_id": "VRX_COMP_03",
                        "rule_name": "Dispute Classification",
                        "status": "PASSED" if dispute_type else "PENDING",
                        "audit_message": f"Classified as {dispute_type.replace('_', ' ')}" if dispute_type else "Classification pending"
                    }
                ],
                "system_status_update": "under_review"
            }
        else:
            return {
                "conversational_response": "Please provide additional details including transaction ID, amount, and the nature of the discrepancy to proceed with compliance analysis.",
                "action_triggered": False,
                "extracted_entities": extracted_data,
                "compliance_checks": [
                    {
                        "rule_id": "VRX_COMP_01",
                        "rule_name": "Transaction ID Validation",
                        "status": "PENDING",
                        "audit_message": "Awaiting transaction identifier"
                    },
                    {
                        "rule_id": "VRX_COMP_02",
                        "rule_name": "Amount Validation",
                        "status": "PENDING",
                        "audit_message": "Awaiting amount confirmation"
                    },
                    {
                        "rule_id": "VRX_COMP_03",
                        "rule_name": "Dispute Classification",
                        "status": "PENDING",
                        "audit_message": "Awaiting dispute classification"
                    }
                ],
                "system_status_update": "open"
            }