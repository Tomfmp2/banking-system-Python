import uuid
from typing import Dict, Any

class WalletKey:
    def __init__(self, key_type: str, key_value: str, account_id: str, key_id: str = None):
        self.key_id = key_id or str(uuid.uuid4())
        self.key_type = key_type # 'email', 'phone', 'alias'
        self.key_value = key_value
        self.account_id = account_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_id": self.key_id,
            "key_type": self.key_type,
            "key_value": self.key_value,
            "account_id": self.account_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WalletKey':
        return cls(
            key_type=data["key_type"],
            key_value=data["key_value"],
            account_id=data["account_id"],
            key_id=data.get("key_id")
        )
