import os

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.json')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
LOANS_FILE = os.path.join(DATA_DIR, 'loans.json')
KEYS_FILE = os.path.join(DATA_DIR, 'keys.json')

# --- BUSINESS RULES LIMITS ---
MIN_INITIAL_DEPOSIT_SAVINGS = 10000.0
MIN_INITIAL_DEPOSIT_CHECKING = 50000.0
MAX_DEPOSIT_AMOUNT = 50000000.0
MAX_DAILY_WITHDRAWAL = 3000000.0
DEFAULT_OVERDRAFT_LIMIT = 500000.0
MIN_TRANSFER_AMOUNT = 1000.0
MAX_TRANSFER_AMOUNT = 10000000.0
MAX_PIN_ATTEMPTS = 3
LOCKOUT_TIME_MINUTES = 15

# --- SYSTEM CONSTANTS ---
BRANCH_CODE = "001"
PAGINATION_LIMIT = 10

# --- ANSI COLORS ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- SYSTEM MESSAGES ---
class Messages:
    WELCOME = "SISTEMA BANCARIO CONSOLA v1.0"
    PROMPT = "Ingrese opción >>> "
    ERR_INVALID_OPTION = "Opción inválida. Por favor, intente nuevamente."
    ERR_DATA_CORRUPTION = "Error crítico: Los datos del sistema están corruptos."
    SUCCESS_LOGIN = "Inicio de sesión exitoso."
