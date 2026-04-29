from typing import List, Optional
from models.transaction import Transaction
from models.account import Account
from database.json_handler import JsonHandler
from services.account_service import AccountService
from config import MAX_DEPOSIT_AMOUNT, DEFAULT_OVERDRAFT_LIMIT, MAX_DAILY_WITHDRAWAL, MIN_TRANSFER_AMOUNT, MAX_TRANSFER_AMOUNT
from utils.exceptions import InsufficientFundsError, InvalidAmountError, DailyLimitExceededError, AccountInactiveError
from datetime import datetime

class TransactionService:
    def __init__(self, tx_db: JsonHandler, account_service: AccountService):
        self.db = tx_db
        self.account_service = account_service

    def get_all_transactions(self) -> List[Transaction]:
        """Obtiene todas las transacciones de la DB."""
        data = self.db.read()
        return [Transaction.from_dict(tx) for tx in data.get("transactions", [])]

    def _save_transactions(self, transactions: List[Transaction]) -> None:
        """Guarda la lista completa de transacciones."""
        tx_dict = [tx.to_dict() for tx in transactions]
        self.db.write("transactions", tx_dict)

    def _append_transaction(self, tx: Transaction) -> None:
        """Agrega una transacción al historial."""
        transactions = self.get_all_transactions()
        transactions.append(tx)
        self._save_transactions(transactions)

    def get_account_history(self, account_id: str) -> List[Transaction]:
        """Obtiene el historial de una cuenta en orden descendente (más recientes primero)."""
        transactions = self.get_all_transactions()
        acc_txs = [tx for tx in transactions if tx.account_id == account_id or tx.target_account_id == account_id]
        return sorted(acc_txs, key=lambda x: x.timestamp, reverse=True)

    def _get_daily_withdrawal_total(self, account_id: str) -> float:
        """Calcula el total retirado en el día actual."""
        today = datetime.now().date()
        history = self.get_account_history(account_id)
        total = 0.0
        for tx in history:
            if tx.transaction_type == 'retiro' and tx.account_id == account_id and tx.status == 'exitosa':
                tx_date = datetime.fromisoformat(tx.timestamp).date()
                if tx_date == today:
                    total += tx.amount
        return total

    def deposit(self, account: Account, amount: float) -> Transaction:
        """Realiza un depósito en una cuenta."""
        if not account.is_active:
            raise AccountInactiveError("No se puede depositar. La cuenta está inactiva.")
            
        if amount <= 1000.0:
            raise InvalidAmountError("El monto a depositar debe ser mayor a $1,000 COP.")
        if amount > MAX_DEPOSIT_AMOUNT:
            raise InvalidAmountError(f"El depósito excede el límite máximo por transacción (${MAX_DEPOSIT_AMOUNT:,.2f}).")
            
        balance_before = account.balance
        account.balance += amount
        self.account_service.update_account(account)
        
        tx = Transaction(
            account_id=account.account_id,
            transaction_type="deposito",
            amount=amount,
            balance_before=balance_before,
            balance_after=account.balance,
            description="Depósito en efectivo"
        )
        self._append_transaction(tx)
        return tx

    def withdraw(self, account: Account, amount: float, pin: str) -> Transaction:
        """Realiza un retiro verificando saldo y límites."""
        if not account.is_active:
            raise AccountInactiveError("La cuenta está inactiva.")
            
        if amount <= 0:
            raise InvalidAmountError("El monto debe ser positivo.")
            
        daily_total = self._get_daily_withdrawal_total(account.account_id)
        if daily_total + amount > MAX_DAILY_WITHDRAWAL:
            raise DailyLimitExceededError(f"Excede límite diario de retiros (${MAX_DAILY_WITHDRAWAL:,.2f}).")
            
        # Validar fondos
        if account.account_type == 'ahorros':
            if account.balance < amount:
                raise InsufficientFundsError("Saldo insuficiente para realizar el retiro.")
        elif account.account_type == 'corriente':
            if account.balance + DEFAULT_OVERDRAFT_LIMIT < amount:
                raise InsufficientFundsError("Monto supera el saldo y el límite de descubierto permitido.")

        # Verificar PIN antes de procesar
        self.account_service.verify_pin(account, pin)
        
        balance_before = account.balance
        account.balance -= amount
        self.account_service.update_account(account)
        
        tx = Transaction(
            account_id=account.account_id,
            transaction_type="retiro",
            amount=amount,
            balance_before=balance_before,
            balance_after=account.balance,
            description="Retiro en efectivo"
        )
        self._append_transaction(tx)
        return tx

    def transfer(self, from_account: Account, target_account_number: str, amount: float, pin: str, description: str = "") -> List[Transaction]:
        """Realiza transferencia atómica entre dos cuentas."""
        if amount < MIN_TRANSFER_AMOUNT:
            raise InvalidAmountError(f"El monto mínimo de transferencia es ${MIN_TRANSFER_AMOUNT:,.2f}.")
        if amount > MAX_TRANSFER_AMOUNT:
            raise InvalidAmountError(f"El monto máximo por transferencia es ${MAX_TRANSFER_AMOUNT:,.2f}.")
            
        if from_account.account_number == target_account_number:
            raise InvalidAmountError("No puede transferir a su propia cuenta.")
            
        target_account = self.account_service.find_by_number(target_account_number)
        
        if not target_account.is_active:
            raise AccountInactiveError("La cuenta destino se encuentra inactiva.")
            
        if from_account.account_type == 'ahorros' and from_account.balance < amount:
            raise InsufficientFundsError("Saldo insuficiente en cuenta origen.")
        elif from_account.account_type == 'corriente' and from_account.balance + DEFAULT_OVERDRAFT_LIMIT < amount:
            raise InsufficientFundsError("Saldo insuficiente (incluyendo descubierto) en cuenta origen.")
            
        self.account_service.verify_pin(from_account, pin)
        
        # Ejecutar atómicamente
        from_balance_before = from_account.balance
        target_balance_before = target_account.balance
        
        try:
            from_account.balance -= amount
            target_account.balance += amount
            
            # Guardamos ambas, si alguna falla se revierten en memoria (la DB no se escribe si hay excepción aquí)
            self.account_service.update_account(from_account)
            self.account_service.update_account(target_account)
            
        except Exception as e:
            # Reversión en caso de fallo crítico en update
            from_account.balance = from_balance_before
            target_account.balance = target_balance_before
            self.account_service.update_account(from_account)
            self.account_service.update_account(target_account)
            raise e

        # Registrar transacciones
        desc = description if description else f"Transferencia a {target_account.owner_name}"
        tx_out = Transaction(
            account_id=from_account.account_id,
            target_account_id=target_account.account_id,
            transaction_type="transferencia",
            amount=amount,
            balance_before=from_balance_before,
            balance_after=from_account.balance,
            description=desc
        )
        
        tx_in = Transaction(
            account_id=target_account.account_id,
            target_account_id=from_account.account_id, # Para rastreo inverso
            transaction_type="transferencia_recibida",
            amount=amount,
            balance_before=target_balance_before,
            balance_after=target_account.balance,
            description=f"Transferencia de {from_account.owner_name}"
        )
        
        # Append ambos
        transactions = self.get_all_transactions()
        transactions.append(tx_out)
        transactions.append(tx_in)
        self._save_transactions(transactions)
        
        return [tx_out, tx_in]
