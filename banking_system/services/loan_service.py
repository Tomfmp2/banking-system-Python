from typing import List
from models.loan import Loan
from models.account import Account
from database.json_handler import JsonHandler
from utils.exceptions import BankException

class LoanService:
    def __init__(self, db_handler: JsonHandler):
        self.db = db_handler

    def get_all_loans(self) -> List[Loan]:
        data = self.db.read()
        return [Loan.from_dict(l) for l in data.get("loans", [])]

    def _save_loans(self, loans: List[Loan]) -> None:
        self.db.write("loans", [l.to_dict() for l in loans])

    def get_loans_by_account(self, account_id: str) -> List[Loan]:
        return [l for l in self.get_all_loans() if l.account_id == account_id]

    def calculate_installment(self, principal: float, monthly_rate: float, months: int) -> float:
        if monthly_rate == 0:
            return principal / months
        return principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)

    def request_loan(self, account: Account, loan_type: str, principal: float, months: int, monthly_income: float) -> Loan:
        # Define rates
        rates = {
            "libranza": 0.012,
            "libre_inversion": 0.02,
            "vehicular": 0.015,
            "vivienda": 0.009
        }
        
        rate = rates.get(loan_type, 0.02)
        installment = self.calculate_installment(principal, rate, months)
        
        # Validation: Cuota <= 30% del ingreso
        status = "activo"
        if installment > monthly_income * 0.30:
            status = "rechazado"
            
        loan = Loan(
            account_id=account.account_id,
            loan_type=loan_type,
            principal=principal,
            interest_rate=rate,
            term_months=months,
            monthly_installment=installment,
            status=status
        )
        
        loans = self.get_all_loans()
        loans.append(loan)
        self._save_loans(loans)
        
        return loan

    def pay_installment(self, account: Account, loan_id: str, amount: float, account_service, transaction_service) -> Loan:
        loans = self.get_all_loans()
        for l in loans:
            if l.loan_id == loan_id and l.account_id == account.account_id:
                if l.status != "activo":
                    raise BankException("El crédito no está activo.")
                
                if amount > l.remaining_balance:
                    amount = l.remaining_balance
                    
                if account.balance < amount:
                    raise BankException("Saldo insuficiente en su cuenta para realizar este pago.")
                    
                # Deduct from account balance
                balance_before = account.balance
                account.balance -= amount
                account_service.update_account(account)
                
                # Record transaction
                from models.transaction import Transaction
                tx = Transaction(
                    account_id=account.account_id,
                    transaction_type="pago_credito",
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=account.balance,
                    description=f"Pago cuota crédito {l.loan_type.capitalize()}"
                )
                txs = transaction_service.get_all_transactions()
                txs.append(tx)
                transaction_service._save_transactions(txs)
                
                l.remaining_balance -= amount
                if l.remaining_balance <= 0.01:
                    l.remaining_balance = 0
                    l.status = "pagado"
                    
                self._save_loans(loans)
                return l
                
        raise BankException("Crédito no encontrado.")
