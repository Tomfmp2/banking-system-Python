from datetime import datetime
import uuid
from typing import Dict, Any, Optional

class Account:
    """
    Representa una cuenta bancaria dentro del sistema.
    """
    def __init__(self,
                 owner_name: str,
                 owner_id: str,
                 account_type: str,
                 balance: float,
                 pin: str,
                 phone: str = "",
                 email: str = "",
                 account_id: Optional[str] = None,
                 account_number: Optional[str] = None,
                 is_active: bool = True,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 failed_pin_attempts: int = 0,
                 locked_until: Optional[str] = None):
        
        self.account_id = account_id if account_id else str(uuid.uuid4())
        self.account_number = account_number
        self.owner_name = owner_name
        self.owner_id = owner_id
        self.account_type = account_type
        self.balance = balance
        self.pin = pin
        self.phone = phone
        self.email = email
        self.is_active = is_active
        
        current_time = datetime.now().isoformat()
        self.created_at = created_at if created_at else current_time
        self.updated_at = updated_at if updated_at else current_time
        
        self.failed_pin_attempts = failed_pin_attempts
        self.locked_until = locked_until

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la cuenta a un diccionario."""
        return {
            "account_id": self.account_id,
            "account_number": self.account_number,
            "owner_name": self.owner_name,
            "owner_id": self.owner_id,
            "account_type": self.account_type,
            "balance": self.balance,
            "pin": self.pin,
            "phone": self.phone,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "failed_pin_attempts": self.failed_pin_attempts,
            "locked_until": self.locked_until
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        """Crea una instancia de Account desde un diccionario."""
        return cls(
            account_id=data.get("account_id"),
            account_number=data.get("account_number"),
            owner_name=data.get("owner_name"),
            owner_id=data.get("owner_id"),
            account_type=data.get("account_type"),
            balance=data.get("balance"),
            pin=data.get("pin"),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            failed_pin_attempts=data.get("failed_pin_attempts", 0),
            locked_until=data.get("locked_until")
        )

    def is_locked(self) -> bool:
        """Determina si la cuenta está bloqueada temporalmente o inactiva."""
        if not self.is_active:
            return True
        if self.locked_until:
            lock_time = datetime.fromisoformat(self.locked_until)
            if datetime.now() < lock_time:
                return True
            else:
                # El bloqueo ha expirado
                self.locked_until = None
                self.failed_pin_attempts = 0
                return False
        return False

    def days_since_created(self) -> int:
        """Retorna la cantidad de días desde la creación de la cuenta."""
        creation_date = datetime.fromisoformat(self.created_at)
        delta = datetime.now() - creation_date
        return delta.days

    @staticmethod
    def generate_account_number(branch_code: str, sequential_id: int) -> str:
        """
        Genera un número de cuenta con dígito verificador.
        Formato: XXX-NNNNNN-YY
        """
        seq_str = f"{sequential_id:06d}"
        # Calculamos un dígito verificador simple sumando los dígitos y aplicando módulo 99
        sum_digits = sum(int(d) for d in seq_str) + sum(int(d) for d in branch_code)
        check_digits = f"{(sum_digits % 99):02d}"
        return f"{branch_code}-{seq_str}-{check_digits}"
