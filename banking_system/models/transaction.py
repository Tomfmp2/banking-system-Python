from datetime import datetime
import uuid
from typing import Dict, Any, Optional

class Transaction:
    """
    Representa una transacción o movimiento financiero en una cuenta.
    """
    def __init__(self,
                 account_id: str,
                 transaction_type: str,
                 amount: float,
                 balance_before: float,
                 balance_after: float,
                 description: str,
                 status: str = 'exitosa',
                 target_account_id: Optional[str] = None,
                 transaction_id: Optional[str] = None,
                 timestamp: Optional[str] = None):
        
        self.transaction_id = transaction_id if transaction_id else str(uuid.uuid4())
        self.account_id = account_id
        self.target_account_id = target_account_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.balance_before = balance_before
        self.balance_after = balance_after
        self.description = description
        self.status = status
        self.timestamp = timestamp if timestamp else datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la transacción a un diccionario."""
        return {
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "target_account_id": self.target_account_id,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "balance_before": self.balance_before,
            "balance_after": self.balance_after,
            "description": self.description,
            "timestamp": self.timestamp,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Crea una instancia de Transaction desde un diccionario."""
        return cls(
            transaction_id=data.get("transaction_id"),
            account_id=data.get("account_id"),
            target_account_id=data.get("target_account_id"),
            transaction_type=data.get("transaction_type"),
            amount=data.get("amount"),
            balance_before=data.get("balance_before"),
            balance_after=data.get("balance_after"),
            description=data.get("description"),
            status=data.get("status", "exitosa"),
            timestamp=data.get("timestamp")
        )
