import sys
import os

# Aseguramos que el directorio raíz está en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import ACCOUNTS_FILE, TRANSACTIONS_FILE, PRODUCTS_FILE, LOANS_FILE, KEYS_FILE
from database import JsonHandler
from services.account_service import AccountService
from services.transaction_service import TransactionService
from services.product_service import ProductService
from services.loan_service import LoanService
from services.key_transfer_service import KeyTransferService
from ui.menu import MenuController

def main():
    """Punto de entrada principal de la aplicación."""
    try:
        # Inicialización de bases de datos
        account_db = JsonHandler(
            file_path=ACCOUNTS_FILE,
            default_structure={"accounts": [], "metadata": {"total_accounts": 0, "last_updated": ""}}
        )
        transaction_db = JsonHandler(
            file_path=TRANSACTIONS_FILE,
            default_structure={"transactions": [], "metadata": {"total_transactions": 0, "last_updated": ""}}
        )
        product_db = JsonHandler(
            file_path=PRODUCTS_FILE,
            default_structure={"products": []}
        )
        loan_db = JsonHandler(
            file_path=LOANS_FILE,
            default_structure={"loans": []}
        )
        key_db = JsonHandler(
            file_path=KEYS_FILE,
            default_structure={"keys": []}
        )
        
        # Inicialización de servicios (Inyección de dependencias)
        account_service = AccountService(account_db)
        transaction_service = TransactionService(transaction_db, account_service)
        product_service = ProductService(product_db)
        loan_service = LoanService(loan_db)
        key_service = KeyTransferService(key_db, account_service, transaction_service)
        
        # Inicializar UI
        menu = MenuController(account_service, transaction_service, product_service, loan_service, key_service)
        menu.run()
        
    except KeyboardInterrupt:
        print("\nSaliendo del sistema de forma segura...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
