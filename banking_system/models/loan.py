import uuid
from typing import Dict, Any
from datetime import datetime

class Loan:
    def __init__(self, account_id: str, loan_type: str, principal: float, interest_rate: float, term_months: int, monthly_installment: float, loan_id: str = None, remaining_balance: float = None, status: str = "activo", created_at: str = None, fondos_disponibles: float = None):
        self.loan_id = loan_id or str(uuid.uuid4())
        self.account_id = account_id
        self.loan_type = loan_type # libranza, libre_inversion, vehicular, vivienda
        self.principal = principal
        self.interest_rate = interest_rate # monthly e.g. 0.015 for 1.5%
        self.term_months = term_months
        self.monthly_installment = monthly_installment
        self.remaining_balance = remaining_balance if remaining_balance is not None else principal
        self.fondos_disponibles = fondos_disponibles if fondos_disponibles is not None else principal
        self.status = status # activo, pagado, rechazado
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loan_id": self.loan_id,
            "account_id": self.account_id,
            "loan_type": self.loan_type,
            "principal": self.principal,
            "interest_rate": self.interest_rate,
            "term_months": self.term_months,
            "monthly_installment": self.monthly_installment,
            "remaining_balance": self.remaining_balance,
            "fondos_disponibles": self.fondos_disponibles,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Loan':
        return cls(
            account_id=data["account_id"],
            loan_type=data["loan_type"],
            principal=data["principal"],
            interest_rate=data["interest_rate"],
            term_months=data["term_months"],
            monthly_installment=data["monthly_installment"],
            loan_id=data.get("loan_id"),
            remaining_balance=data.get("remaining_balance"),
            status=data.get("status", "activo"),
            created_at=data.get("created_at"),
            fondos_disponibles=data.get("fondos_disponibles")
        )
