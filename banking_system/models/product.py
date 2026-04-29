import uuid
from typing import Dict, Any
from datetime import datetime

class Product:
    def __init__(self, account_id: str, product_category: str, product_type: str, details: Dict[str, Any], product_id: str = None, status: str = "activo", created_at: str = None):
        self.product_id = product_id or str(uuid.uuid4())
        self.account_id = account_id
        self.product_category = product_category # ahorro, inversion, tarjeta
        self.product_type = product_type
        self.details = details # metadata specifics
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "account_id": self.account_id,
            "product_category": self.product_category,
            "product_type": self.product_type,
            "details": self.details,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        return cls(
            account_id=data["account_id"],
            product_category=data["product_category"],
            product_type=data["product_type"],
            details=data.get("details", {}),
            product_id=data.get("product_id"),
            status=data.get("status", "activo"),
            created_at=data.get("created_at")
        )
