import hashlib
from typing import List, Optional
from models.account import Account
from database.json_handler import JsonHandler
from config import MIN_INITIAL_DEPOSIT_SAVINGS, MIN_INITIAL_DEPOSIT_CHECKING, BRANCH_CODE, MAX_PIN_ATTEMPTS, LOCKOUT_TIME_MINUTES
from utils.exceptions import AccountNotFoundError, DuplicateAccountError, InvalidAmountError, InvalidPinError, AccountInactiveError
from datetime import datetime, timedelta

class AccountService:
    def __init__(self, db_handler: JsonHandler):
        self.db = db_handler

    def _hash_pin(self, pin: str, account_id: str) -> str:
        """Aplica hash SHA-256 usando account_id como salt."""
        salt = account_id.encode('utf-8')
        pin_encoded = pin.encode('utf-8')
        return hashlib.sha256(salt + pin_encoded).hexdigest()

    def get_all_accounts(self) -> List[Account]:
        """Obtiene todas las cuentas desde la DB."""
        data = self.db.read()
        return [Account.from_dict(acc) for acc in data.get("accounts", [])]

    def _save_accounts(self, accounts: List[Account]) -> None:
        """Guarda la lista de cuentas en la DB."""
        accounts_dict = [acc.to_dict() for acc in accounts]
        self.db.write("accounts", accounts_dict)

    def find_by_number(self, account_number: str) -> Account:
        """Busca una cuenta por su número."""
        accounts = self.get_all_accounts()
        for acc in accounts:
            if acc.account_number == account_number:
                return acc
        raise AccountNotFoundError(f"La cuenta {account_number} no existe.")

    def find_by_id(self, account_id: str) -> Account:
        """Busca una cuenta por su ID interno."""
        accounts = self.get_all_accounts()
        for acc in accounts:
            if acc.account_id == account_id:
                return acc
        raise AccountNotFoundError("Cuenta no encontrada.")

    def update_account(self, updated_account: Account) -> None:
        """Actualiza una cuenta en la base de datos."""
        updated_account.updated_at = datetime.now().isoformat()
        accounts = self.get_all_accounts()
        for i, acc in enumerate(accounts):
            if acc.account_id == updated_account.account_id:
                accounts[i] = updated_account
                self._save_accounts(accounts)
                return
        raise AccountNotFoundError("No se puede actualizar. Cuenta no encontrada.")

    def create_account(self, owner_name: str, owner_id: str, account_type: str, initial_deposit: float, pin: str, phone: str = "", email: str = "") -> Account:
        """Crea una nueva cuenta aplicando reglas de negocio."""
        accounts = self.get_all_accounts()
        
        # Validar multiplicidad (Regla 01)
        for acc in accounts:
            if acc.owner_id == owner_id and acc.account_type == account_type:
                raise DuplicateAccountError(f"El titular ya posee una cuenta tipo {account_type}.")
                
        # Validar depósito inicial (Regla 02)
        if account_type == 'ahorros' and initial_deposit < MIN_INITIAL_DEPOSIT_SAVINGS:
            raise InvalidAmountError(f"El depósito mínimo para ahorros es ${MIN_INITIAL_DEPOSIT_SAVINGS:,.2f}")
        if account_type == 'corriente' and initial_deposit < MIN_INITIAL_DEPOSIT_CHECKING:
            raise InvalidAmountError(f"El depósito mínimo para corriente es ${MIN_INITIAL_DEPOSIT_CHECKING:,.2f}")

        # Secuencial y generación de número de cuenta (Regla 03)
        sequential_id = len(accounts) + 1
        account_number = Account.generate_account_number(BRANCH_CODE, sequential_id)
        
        # Crear cuenta temporal para generar ID (usado como salt)
        new_account = Account(
            owner_name=owner_name,
            owner_id=owner_id,
            account_type=account_type,
            balance=initial_deposit,
            pin="", # se setea después del hash
            phone=phone,
            email=email,
            account_number=account_number
        )
        
        # Hashear PIN
        new_account.pin = self._hash_pin(pin, new_account.account_id)
        
        accounts.append(new_account)
        self._save_accounts(accounts)
        return new_account

    def authenticate(self, account_number: str, pin: str) -> Account:
        """Verifica credenciales y gestiona bloqueos por intentos fallidos."""
        acc = self.find_by_number(account_number)
        
        if acc.is_locked():
            raise AccountInactiveError("Su cuenta se encuentra bloqueada por seguridad o está inactiva.")

        hashed_pin = self._hash_pin(pin, acc.account_id)
        if acc.pin != hashed_pin:
            acc.failed_pin_attempts += 1
            if acc.failed_pin_attempts >= MAX_PIN_ATTEMPTS:
                lock_time = datetime.now() + timedelta(minutes=LOCKOUT_TIME_MINUTES)
                acc.locked_until = lock_time.isoformat()
                self.update_account(acc)
                raise AccountInactiveError(f"Demasiados intentos fallidos. Cuenta bloqueada por {LOCKOUT_TIME_MINUTES} minutos.")
            
            self.update_account(acc)
            raise InvalidPinError(f"PIN incorrecto. Intentos restantes: {MAX_PIN_ATTEMPTS - acc.failed_pin_attempts}")
            
        # Resetea intentos si es correcto
        if acc.failed_pin_attempts > 0:
            acc.failed_pin_attempts = 0
            self.update_account(acc)
            
        return acc

    def verify_pin(self, account: Account, pin: str) -> None:
        """Verifica el PIN para una operación (retiro, transferencia)."""
        hashed_pin = self._hash_pin(pin, account.account_id)
        if account.pin != hashed_pin:
            raise InvalidPinError("El PIN ingresado es incorrecto.")
