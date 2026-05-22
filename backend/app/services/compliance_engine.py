import re
from typing import List, Dict, Any
from ..models.schemas import ComplianceOutputSchema

class ComplianceEngine:
    
    def __init__(self):
        self.rules = {
            "VRX_COMP_01": {
                "name": "Transaction ID Validation",
                "pattern": r'^[A-Za-z0-9\-_]{8,36}$'
            },
            "VRX_COMP_02": {
                "name": "Amount Range Validation",
                "min_amount": 0.01,
                "max_amount": 999999.99
            },
            "VRX_COMP_03": {
                "name": "Dispute Classification",
                "valid_types": ['double_deduction', 'invoice_mismatch', 'refund_pending']
            }
        }
    
    def validate_transaction_id(self, transaction_id: str) -> ComplianceOutputSchema:
        pattern = self.rules["VRX_COMP_01"]["pattern"]
        is_valid = bool(re.match(pattern, transaction_id)) if transaction_id else False
        
        return ComplianceOutputSchema(
            rule_id="VRX_COMP_01",
            rule_name=self.rules["VRX_COMP_01"]["name"],
            status="PASSED" if is_valid else "FAILED",
            audit_message=f"Transaction ID format validation: {'valid format detected' if is_valid else 'invalid format - expected alphanumeric with hyphens or underscores, length 8-36 characters'}"
        )
    
    def validate_amount(self, amount: float) -> ComplianceOutputSchema:
        min_amt = self.rules["VRX_COMP_02"]["min_amount"]
        max_amt = self.rules["VRX_COMP_02"]["max_amount"]
        is_valid = min_amt <= amount <= max_amt
        
        return ComplianceOutputSchema(
            rule_id="VRX_COMP_02",
            rule_name=self.rules["VRX_COMP_02"]["name"],
            status="PASSED" if is_valid else "FAILED",
            audit_message=f"Amount validation: {'within acceptable range' if is_valid else f'exceeds bounds (valid range: ${min_amt:,.2f} - ${max_amt:,.2f})'}"
        )
    
    def validate_dispute_type(self, dispute_type: str) -> ComplianceOutputSchema:
        valid_types = self.rules["VRX_COMP_03"]["valid_types"]
        is_valid = dispute_type in valid_types
        
        # Fixed f-string syntax error
        valid_types_str = ", ".join(valid_types)
        if is_valid:
            audit_message = f"Dispute classification: valid dispute category - {dispute_type}"
        else:
            audit_message = f"Dispute classification: invalid type - must be one of: {valid_types_str}"
        
        return ComplianceOutputSchema(
            rule_id="VRX_COMP_03",
            rule_name=self.rules["VRX_COMP_03"]["name"],
            status="PASSED" if is_valid else "FAILED",
            audit_message=audit_message
        )
    
    def run_checks(self, transaction_id: str, amount: float, dispute_type: str) -> List[ComplianceOutputSchema]:
        checks = []
        checks.append(self.validate_transaction_id(transaction_id))
        checks.append(self.validate_amount(amount))
        checks.append(self.validate_dispute_type(dispute_type))
        return checks
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {
            "transaction_id": None,
            "amount": 0.0,
            "dispute_type": None
        }
        
        # Extract transaction ID patterns
        tx_pattern = r'(?:txn|transaction|id)[:\s]*([A-Za-z0-9\-_]{8,36})'
        tx_match = re.search(tx_pattern, text.lower())
        if tx_match:
            entities["transaction_id"] = tx_match.group(1)
        
        # Extract amounts with currency symbols
        amount_pattern = r'(?:amount|charge|deduction|payment)[:\s]*\$?(\d+(?:\.\d{2})?)'
        amount_match = re.search(amount_pattern, text.lower())
        if amount_match:
            entities["amount"] = float(amount_match.group(1))
        
        # Determine dispute type
        if "double" in text.lower() or "duplicate" in text.lower():
            entities["dispute_type"] = "double_deduction"
        elif "invoice" in text.lower() or "bill" in text.lower():
            entities["dispute_type"] = "invoice_mismatch"
        elif "refund" in text.lower() or "pending" in text.lower():
            entities["dispute_type"] = "refund_pending"
        
        return entities