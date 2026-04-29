from typing import List
from models.wallet_key import WalletKey
from models.account import Account
from database.json_handler import JsonHandler
from services.account_service import AccountService
from services.transaction_service import TransactionService
from utils.exceptions import BankException

class KeyTransferService:
    def __init__(self, db_handler: JsonHandler, account_service: AccountService, transaction_service: TransactionService):
        self.db = db_handler
        self.account_service = account_service
        self.transaction_service = transaction_service

    def get_all_keys(self) -> List[WalletKey]:
        data = self.db.read()
        return [WalletKey.from_dict(k) for k in data.get("keys", [])]

    def _save_keys(self, keys: List[WalletKey]) -> None:
        self.db.write("keys", [k.to_dict() for k in keys])

    def get_keys_by_account(self, account_id: str) -> List[WalletKey]:
        return [k for k in self.get_all_keys() if k.account_id == account_id]

    def register_key(self, account: Account, key_type: str, key_value: str) -> WalletKey:
        keys = self.get_all_keys()
        
        # Validation: No duplicate keys across the system
        for k in keys:
            if k.key_value.lower() == key_value.lower():
                raise BankException("Esta llave ya se encuentra registrada por otro usuario.")
                
        new_key = WalletKey(key_type=key_type, key_value=key_value, account_id=account.account_id)
        keys.append(new_key)
        self._save_keys(keys)
        return new_key

    def resolve_key(self, key_value: str) -> Account:
        keys = self.get_all_keys()
        for k in keys:
            if k.key_value.lower() == key_value.lower():
                return self.account_service.find_by_id(k.account_id)
        raise BankException("Llave no encontrada.")

    def transfer_by_key(self, source_account: Account, key_value: str, amount: float, pin: str, description: str = ""):
        target_account = self.resolve_key(key_value)
        if target_account.account_id == source_account.account_id:
            raise BankException("No puede transferirse a sí mismo mediante llave.")
            
        return self.transaction_service.transfer(source_account, target_account.account_number, amount, pin, description)
